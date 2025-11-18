# Redis 网络架构与事件循环

## 概述

Redis 基于事件驱动的单线程服务器（主线程执行命令）。本文档详细分析网络架构、事件循环机制和多路复用实现。

---

## 网络架构

### 监听器初始化

**文件:** `src/server.c:initListeners()`

```c
void initListeners(void) {
    // 1. 配置 TCP/TLS/Unix Socket 监听器
    if (server.port != 0) {
        listener->bindaddr = server.bindaddr;
        listener->port = server.port;
        listener->ct = connectionByType(CONN_TYPE_SOCKET);
    }
    
    if (server.tls_port != 0) {
        listener->port = server.tls_port;
        listener->ct = connectionByType(CONN_TYPE_TLS);
    }
    
    if (server.unixsocket != NULL) {
        listener->ct = connectionByType(CONN_TYPE_UNIX);
    }
    
    // 2. 创建监听套接字并注册accept事件处理器
    for (int j = 0; j < CONN_TYPE_MAX; j++) {
        listener = &server.listeners[j];
        if (listener->ct == NULL) continue;
        
        // 监听端口
        connListen(listener);
        
        // 注册accept事件处理器
        createSocketAcceptHandler(listener, connAcceptHandler(listener->ct));
    }
}
```

### 端口绑定

**文件:** `src/server.c:listenToPort()`

```c
int listenToPort(connListener *sfd) {
    for (j = 0; j < sfd->bindaddr_count; j++) {
        char* addr = bindaddr[j];
        
        if (strchr(addr,':')) {
            // IPv6 地址
            sfd->fd[sfd->count] = anetTcp6Server(port, addr, server.tcp_backlog);
        } else {
            // IPv4 地址
            sfd->fd[sfd->count] = anetTcpServer(port, addr, server.tcp_backlog);
        }
        
        // 设置为非阻塞
        anetNonBlock(NULL, sfd->fd[sfd->count]);
        anetCloexec(sfd->fd[sfd->count]); // close-on-exec
        
        sfd->count++;
    }
    return C_OK;
}
```

### 接受连接

**文件:** `src/socket.c:connSocketAcceptHandler()`

```c
static void connSocketAcceptHandler(aeEventLoop *el, int fd, void *privdata, int mask) {
    int max = server.max_new_conns_per_cycle;
    
    while(max--) {
        // 接受连接
        cfd = anetTcpAccept(fd, cip, sizeof(cip), &cport);
        if (cfd == ANET_ERR) {
            if (errno == EWOULDBLOCK) return;
            continue;
        }
        
        // 创建客户端
        conn = connCreateAcceptedSocket(el, cfd, NULL);
        
        // 处理新连接
        acceptCommonHandler(conn, 0, cip);
    }
}
```

---

## 事件循环

### 事件循环初始化

**文件:** `src/server.c:initServer()`

```c
void initServer(void) {
    // 创建事件循环
    server.el = aeCreateEventLoop(server.maxclients + CONFIG_FDSET_INCR);
    
    // 设置before/after sleep回调
    server.el->beforesleep = beforeSleep;
    server.el->aftersleep = afterSleep;
}

// InitServerLast 中初始化IO线程
void InitServerLast(void) {
    bioInit();
    initThreadedIO();  // ← 初始化IO线程池
    set_jemalloc_bg_thread(server.jemalloc_bg_thread);
}
```

### 主事件循环

**文件:** `src/ae.c:aeMain()`

```c
void aeMain(aeEventLoop *eventLoop) {
    eventLoop->stop = 0;
    
    while (!eventLoop->stop) {
        // 处理就绪事件
        aeProcessEvents(eventLoop, AE_ALL_EVENTS|
                                   AE_CALL_BEFORE_SLEEP|
                                   AE_CALL_AFTER_SLEEP);
    }
}
```

### 事件处理

**文件:** `src/ae.c:aeProcessEvents()`

```c
int aeProcessEvents(aeEventLoop *eventLoop, int flags) {
    int processed = 0;
    
    // 1. 计算时间事件超时
    if (flags & AE_TIME_EVENTS && !(flags & AE_DONT_WAIT)) {
        aeTimeEvent *shortest = aeSearchNearestTimer(eventLoop);
        if (shortest) {
            long now_sec, now_ms;
            aeGetTime(&now_sec, &now_ms);
            struct timeval tv;
            long long ms = (shortest->when_sec - now_sec)*1000 +
                           (shortest->when_ms - now_ms);
            
            if (ms > 0) {
                tv.tv_sec = ms/1000;
                tv.tv_usec = (ms % 1000)*1000;
            } else {
                tv.tv_sec = 0;
                tv.tv_usec = 0;
            }
        }
    }
    
    // 2. 调用 beforeSleep
    if (eventLoop->beforesleep != NULL && flags & AE_CALL_BEFORE_SLEEP)
        eventLoop->beforesleep(eventLoop);
    
    // 3. 处理文件事件（网络I/O）
    int numevents = aeApiPoll(eventLoop, tvp);
    
    for (j = 0; j < numevents; j++) {
        aeFileEvent *fe = &eventLoop->events[eventLoop->fired[j].fd];
        int mask = eventLoop->fired[j].mask;
        int fd = eventLoop->fired[j].fd;
        
        // 可读事件
        if (fe->mask & mask & AE_READABLE) {
            rfired = 1;
            fe->rfileProc(eventLoop, fd, fe->clientData, mask);
        }
        
        // 可写事件
        if (fe->mask & mask & AE_WRITABLE) {
            if (!rfired || fe->wfileProc != fe->rfileProc)
                fe->wfileProc(eventLoop, fd, fe->clientData, mask);
        }
        
        processed++;
    }
    
    // 4. 调用 afterSleep
    if (eventLoop->aftersleep != NULL && flags & AE_CALL_AFTER_SLEEP)
        eventLoop->aftersleep(eventLoop);
    
    // 5. 处理时间事件
    if (flags & AE_TIME_EVENTS)
        processed += processTimeEvents(eventLoop);
    
    return processed;
}
```

---

## BeforeSleep / AfterSleep

### beforeSleep

**文件:** `src/server.c:beforeSleep()`

```c
void beforeSleep(aeEventLoop *eventLoop) {
    // 1. 处理被阻塞的客户端
    handleClientsWithPendingReadsUsingThreads();
    
    // 2. 写入pending的写缓冲区
    handleClientsWithPendingWrites();
    
    // 3. 处理客户端挂起读
    handleClientsWithPendingReadsUsingThreads();
    
    // 4. 增加全局命令时间
    updateCachedTime(1);
    
    // 5. 自动过期清理
    evictionPoolPopulate(DICT_MAIN_KEYS);
    
    // 6. 更新统计
    trackInstantaneousMetric(STATS_METRIC_COMMAND, server.stat_numcommands);
}
```

### afterSleep

**文件:** `src/server.c:afterSleep()`

```c
void afterSleep(aeEventLoop *eventLoop) {
    /* Currently nothing. */
}
```

---

## 多路复用机制

### 支持的后端

Redis 根据平台自动选择最优I/O多路复用：

- **Linux**: epoll（高性能，推荐）
- **BSD/Mac**: kqueue（高性能）
- **Solaris**: evport（高性能）
- **其他**: select（通用但性能较低）

### Select 模式实现

**文件:** `src/ae_select.c`

```c
static int aeApiPoll(aeEventLoop *eventLoop, struct timeval *tvp) {
    aeApiState *state = eventLoop->apidata;
    int retval, j, numevents = 0;

    // 复制文件描述符集合，避免select修改原集合
    memcpy(&state->_rfds, &state->rfds, sizeof(fd_set));
    memcpy(&state->_wfds, &state->wfds, sizeof(fd_set));

    // 调用select等待事件
    retval = select(eventLoop->maxfd + 1,
                    &state->_rfds, &state->_wfds, NULL, tvp);
    
    if (retval > 0) {
        // 遍历所有文件描述符，检查哪些有事件
        for (j = 0; j <= eventLoop->maxfd; j++) {
            int mask = 0;
            aeFileEvent *fe = &eventLoop->events[j];

            if (fe->mask == AE_NONE) continue;
            
            // 检查读事件
            if (fe->mask & AE_READABLE && FD_ISSET(j, &state->_rfds))
                mask |= AE_READABLE;
            
            // 检查写事件
            if (fe->mask & AE_WRITABLE && FD_ISSET(j, &state->_wfds))
                mask |= AE_WRITABLE;
            
            // 记录触发的事件
            eventLoop->fired[numevents].fd = j;
            eventLoop->fired[numevents].mask = mask;
            numevents++;
        }
    } else if (retval == -1 && errno != EINTR) {
        panic("aeApiPoll: select, %s", strerror(errno));
    }

    return numevents;
}
```

**Select 模式特点：**

| 特点 | 说明 |
|------|------|
| FD 数量限制 | 通常 1024 |
| 时间复杂度 | O(n) - 需要遍历所有 FD |
| 内存拷贝 | 每次调用都需要拷贝 FD 集合 |
| 适用场景 | 小规模连接（< 1000） |

**优点：**
- 跨平台兼容性好
- 实现简单
- 支持超时机制

**缺点：**
- FD 数量限制（通常 1024）
- O(n) 时间复杂度
- 每次调用需要拷贝 FD 集合
- 性能随 FD 数量线性下降

### Epoll 模式实现

**文件:** `src/ae_epoll.c`

#### 事件添加

```c
static int aeApiAddEvent(aeEventLoop *eventLoop, int fd, int mask) {
    aeApiState *state = eventLoop->apidata;
    struct epoll_event ee = {0};
    
    // 判断是添加还是修改事件
    int op = eventLoop->events[fd].mask == AE_NONE ?
            EPOLL_CTL_ADD : EPOLL_CTL_MOD;

    ee.events = 0;
    mask |= eventLoop->events[fd].mask; // 合并旧事件
    
    // 设置事件类型
    if (mask & AE_READABLE) ee.events |= EPOLLIN;
    if (mask & AE_WRITABLE) ee.events |= EPOLLOUT;
    ee.data.fd = fd;
    
    // 调用epoll_ctl
    if (epoll_ctl(state->epfd, op, fd, &ee) == -1) return -1;
    return 0;
}
```

#### 事件轮询

```c
static int aeApiPoll(aeEventLoop *eventLoop, struct timeval *tvp) {
    aeApiState *state = eventLoop->apidata;
    int retval, numevents = 0;
    
    retval = epoll_wait(state->epfd, state->events, eventLoop->setsize,
                       tvp ? (tvp->tv_sec*1000 + tvp->tv_usec/1000) : -1);
    
    if (retval > 0) {
        int j;
        numevents = retval;
        
        for (j = 0; j < numevents; j++) {
            int mask = 0;
            struct epoll_event *e = state->events + j;
            
            // 转换epoll事件到Redis事件
            if (e->events & EPOLLIN) mask |= AE_READABLE;
            if (e->events & EPOLLOUT) mask |= AE_WRITABLE;
            if (e->events & EPOLLERR) mask |= AE_READABLE | AE_WRITABLE;
            if (e->events & EPOLLHUP) mask |= AE_READABLE | AE_WRITABLE;
            
            eventLoop->fired[j].fd = e->data.fd;
            eventLoop->fired[j].mask = mask;
        }
    }
    
    return numevents;
}
```

**Epoll 模式特点：**

| 特点 | 说明 |
|------|------|
| FD 数量限制 | 无限制 |
| 时间复杂度 | O(1) - 只处理活跃 FD |
| 内存拷贝 | 无，内核直接管理 |
| 适用场景 | 大规模连接（> 1000） |

**优点：**
- 无 FD 数量限制
- O(1) 时间复杂度
- 事件驱动，只处理活跃 FD
- 内存效率高
- 支持边缘触发和水平触发

**缺点：**
- 仅支持 Linux
- 实现相对复杂
- 需要内核支持

### Select vs Epoll 性能对比

| 指标 | Select | Epoll |
|------|--------|-------|
| FD 数量限制 | 1024 | 无限制 |
| 时间复杂度 | O(n) | O(1) |
| 内存使用 | 高 | 低 |
| CPU 使用 | 高 | 低 |
| 适用场景 | 小规模连接 | 大规模连接 |
| 性能随连接增长 | 线性下降 | 保持稳定 |

**性能曲线对比：**

```mermaid
graph LR
    A[连接数] --> B[Select性能]
    A --> C[Epoll性能]
    
    B --> D[线性下降]
    C --> E[保持稳定]
    
    style D fill:#ffebee
    style E fill:#e8f5e8
```

### 多路复用机制选择

Redis 在启动时会自动选择平台支持的最佳多路复用机制：

```c
// 优先级：epoll > kqueue > evport > select
#ifdef HAVE_EPOLL
    #include "ae_epoll.c"  // Linux
#elif defined(HAVE_KQUEUE)
    #include "ae_kqueue.c" // BSD/Mac
#elif defined(HAVE_SOLARIS)
    #include "ae_evport.c" // Solaris
#else
    #include "ae_select.c" // 通用
#endif
```

---

## 服务器组件架构

### 核心组件流程图

```mermaid
graph TD
    subgraph Event Loop[事件循环层]
        A[aeMain<br/>主循环]
        B[aeProcessEvents<br/>处理事件]
        C[beforeSleep<br/>循环前处理]
        D[afterSleep<br/>循环后处理]
    end
    
    subgraph Network[网络层]
        E[initListeners<br/>初始化监听器]
        F[connAcceptHandler<br/>接受连接]
        G[readQueryFromClient<br/>读取请求]
        H[addReply<br/>发送响应]
    end
    
    subgraph Command[命令处理层]
        I[processInputBuffer<br/>解析协议]
        J[processCommand<br/>查找命令]
        K[call<br/>执行命令]
        L[命令实现<br/>setCommand等]
    end
    
    subgraph Storage[存储层]
        M[redisDb<br/>数据库]
        N[dict<br/>键空间字典]
        O[robj<br/>对象系统]
    end
    
    subgraph Background[后台处理]
        P[Bio<br/>后台I/O线程]
        Q[IO Threads<br/>I/O多线程]
        R[Cron<br/>定时任务]
    end
    
    A --> B
    B --> C
    B --> D
    C --> E
    
    F --> G
    G --> I
    I --> J
    J --> K
    K --> L
    L --> M
    M --> N
    N --> O
    
    K --> H
    H --> Network
    
    A --> R
    A --> P
    A --> Q
    
    style A fill:#ff9999
    style K fill:#99ff99
    style M fill:#9999ff
```

### 模块依赖关系

```
Event Loop (ae.c)
    ↓
Network Layer (networking.c, socket.c)
    ↓
Command Layer (server.c:processCommand)
    ↓
Object Layer (object.c, t_*.c)
    ↓
Data Structure (dict.c, sds.c, listpack.c)
    ↓
Memory Management (zmalloc.c)
```

---

## 命令处理完整流程

```mermaid
sequenceDiagram
    participant Client as 客户端
    participant EventLoop as 事件循环
    participant Network as 网络层
    participant Parser as 协议解析
    participant Command as 命令处理
    participant Storage as 存储层
    
    Client->>Network: TCP连接
    Network->>EventLoop: 注册accept事件
    EventLoop->>Network: 触发accept
    Network->>Client: 创建connection
    
    Client->>Network: 发送命令 "SET foo bar"
    Network->>EventLoop: 注册read事件
    EventLoop->>Network: 触发read
    Network->>Parser: readQueryFromClient
    Parser->>Parser: processInputBuffer
    Parser->>Command: argv[] = [SET, foo, bar]
    
    Command->>Command: processCommand
    Command->>Command: lookupCommand
    Command->>Storage: call(setCommand)
    Storage->>Storage: setGenericCommand
    Storage->>Storage: setKey (写入数据库)
    Storage->>Network: addReply("+OK")
    
    Network->>EventLoop: 注册write事件
    EventLoop->>Network: 触发write
    Network->>Client: 发送响应
```

---

## 性能优化

### 1. I/O 多路复用
- 使用 epoll/kqueue 减少系统调用
- 单线程避免锁竞争
- 非阻塞I/O

### 2. I/O 多线程（Redis 6.0+）
- **主线程**：执行命令、操作数据库（单线程保证原子性）
- **IO线程池**：处理网络读写、协议解析
- **读操作**：`io-threads-do-reads yes` 后，IO线程处理读取和解析
- **写操作**：响应写入由IO线程池并发处理

**优势：**
- 利用多核CPU，提升网络I/O吞吐量
- 命令执行仍单线程，无锁竞争
- 适合高并发场景（如缓存、session存储）

### 3. 事件驱动
- 按需注册/注销事件
- 批量处理就绪事件
- 时间事件与文件事件分离

### 4. 批处理
- 一次 `accept` 接受多个连接
- `beforeSleep` 批量处理pending操作
- 批量写入响应

### 5. 零拷贝
- 使用 writev 合并写
- 减少内存复制
- 延迟释放大对象

---

## 总结

Redis 的事件驱动架构特点：

1. **单线程主循环**: 命令执行在主线程，保证原子性
2. **异步I/O**: 通过多路复用实现高并发
3. **事件驱动**: 文件事件+时间事件统一处理
4. **批处理优化**: beforeSleep 处理pending任务
5. **模块化设计**: 清晰的层次划分

相关文档：
- [Redis 服务器架构](redis-server.md)
- [Redis 命令执行流程](redis_cli_cmd.md)
- [Redis 数据类型](redis-data-type.md)
- [Redis 调试指南](redis-debug.md)

