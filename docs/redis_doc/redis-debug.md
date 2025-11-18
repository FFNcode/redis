# Redis 调试指南

本文档介绍如何在 CLion 中调试 Redis 命令执行流程。

## 准备工作

### 1. 编译 Redis（调试模式）

确保使用调试标志编译 Redis：

```bash
cd github/redis-unstable
make clean
make CFLAGS="-g -O0"
```

**重要参数：**
- `-g`: 生成调试符号
- `-O0`: 禁用优化，便于调试

### 2. 配置 CLion

#### 设置编译数据库

确保项目根目录有 `compile_commands.json` 文件。

#### 创建 CMakeLists.txt（可选）

如果需要 CMake 支持，创建 `CMakeLists.txt`：

```cmake
cmake_minimum_required(VERSION 3.10)
project(redis)

set(CMAKE_C_STANDARD 99)
set(CMAKE_C_FLAGS "-g -O0")
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

# 添加所有源文件
file(GLOB_RECURSE SOURCES "src/*.c" "deps/*.c")
include_directories(${CMAKE_CURRENT_SOURCE_DIR}/src)
include_directories(${CMAKE_CURRENT_SOURCE_DIR}/deps)
```

### 3. 创建运行配置

在 CLion 中创建运行配置：

**Run/Debug Configuration:**
- **Target**: redis-server
- **Executable**: `src/redis-server`
- **Program arguments**: `--port 6379`
- **Working directory**: `${PROJECT_DIR}`

---

## 调试 SET foo bar 命令

### 断点位置

在以下关键位置设置断点：

1. **网络接收**: `src/networking.c:2892` - `processInputBuffer()`
2. **命令解析**: `src/server.c:4073` - `processCommand()`
3. **命令执行**: `src/server.c:3712` - `call()`
4. **SET实现**: `src/t_string.c: assignment done` - `setCommand()`
5. **通用逻辑**: `src/t_string.c:82` - `setGenericCommand()`
6. **数据库写入**: `src/db.c` - `setKey()`

### 关键变量监视

在断点处监视以下变量：

```c
// 客户端命令参数
c->argv[0]        // "SET"
c->argv[1]        // key: "foo"
c->argv[2]        // value: "bar"
c->argc           // 参数个数: 3

// 数据库相关
c->db->id         // 数据库编号: 0
c->db->dict       // 键空间字典

// 命令相关
c->cmd->name      // 命令名: "set"
c->cmd->proc      // 函数指针: setCommand

// 数据修改标志
server.dirty      // 是否修改了数据

// 查询缓冲区
c->querybuf       // 原始命令数据
```

### 完整调用栈

调试时的完整调用栈：

```
Frame 5: readQueryFromClient()     # src/networking.c
  → 从socket读取数据到 querybuf

Frame 4: processInputBuffer()      # src/networking.c:2892
  → 解析 RESP 协议，构建 argv[] 数组

Frame 3: processCommand()          # src/server.c:4073
  → 查找命令，登记权限，调用 call()

Frame 2: call()                    # src/server.c:3712
  → 执行命令函数，记录统计信息

Frame 1: setCommand()              # src/t_string.c:382
  → SET命令入口，解析扩展参数

Frame 0: setGenericCommand()       # src/t_string.c:82
  → 执行实际的键值对设置
```

---

## 调试技巧

### 1. 设置条件断点

只在特定条件下停止：

```c
above: 按数字序号列出所有帧（call frames），包括栈上被省略的部分，通常调试时只会显示部分栈帧；使用这个信息可以了解完整的调用上下文。

// 只在处理特定键时停止
c->argv[1]->ptr[0] == 'f'  // key 以 'f' 开头

// 只在修改数据库时停止
server.dirty > 0
```

### 2. 动态修改变量

可以在调试时修改 `c->argv[2]` 来测试不同值：

```
# 在 Debug Console 中
c->argv[2]->ptr = "new_value"
```

### 3. 查看内部结构

```c
// 查看键空间字典
print c->db->dict->ht[0].used       // 键的数量
print c->db->dict->ht[0].size       // 哈希表大小

// 查看对象编码
print c->argv[2]->encoding          // 1=int, 8=embstr, 19=raw
print c->argv[2]->type              // 0=string

// 查看 SDS 字符串
print ((sds) c->querybuf)->len      // 缓冲区长度
print ((sds) c->querybuf)->alloc    // 已分配空间
```

### 4. 日志输出

可以在代码中添加日志：

```c
serverLog(LL_DEBUG, "SET key: %s, value: %s", 
          c->argv[1]->ptr, c->argv[2]->ptr);
```

在 redis.conf 中设置日志级别：

```
loglevel debug
```

---

## 单步调试流程

### 场景：调试 `SET foo bar`

#### 步骤1: 启动服务

1. 在 CLion 中启动 Redis Server（Debug 模式）
2. 在另一个终端连接：
   ```bash
   redis-cli -p 6379
   ```

#### 步骤2: 设置断点

在 `processCommand` 函数入口处设置断点（`src/server.c:4073`）。

#### 步骤3: 发送命令

在 redis-cli 中输入：
```redis
SET foo bar
```

#### 步骤4: 单步执行

**Frame: processCommand**
- 查看 `c->argv[0]` → "SET"
- 查看 `c->argv[1]` → "foo"
- 查看 `c->argv[2]` → "bar"
- 查看 `c->argc` → 3

按 `F7` (Step Into) 进入 `call()` 函数。

**Frame: call**
- 查看 `c->cmd->proc` → `setCommand`
- 查看 `server.dirty` → 0 (修改前)

按 `F7` 进入 `setCommand()`。

**Frame: setCommand**
- 查看 `flags` → 0
- 查看 `expire` → NULL
- 按 `F7` 进入 `setGenericCommand()`。

**Frame: setGenericCommand**
- 查看 `found` → 0 (键不存在)
- 按 `F8` (Step Over) 执行 `setKey()`。
- 查看 `server.dirty` → 1 (修改后)

按 `F9` (Resume) 继续执行，等待下一次断点或命令。

---

## 调试工具

### GDB 命令（在 CLion 调试控制台）

```
# 查看变量
print c->argv[1]
print *c->db

# 查看调用栈
bt
bt full

# 查看内存
x/16c c->argv[1]->ptr    # 显示16个字符
x/16x c->argv[1]         # 显示16个十六进制

# 查看结构体
ptype client
ptype redisDb

# 执行函数
call serverLog(LL_DEBUG, "test")

# 设置观察点
watch server.dirty

# 条件断点
break t_string.c:382 if c->argv[1]->ptr[0] == 'f'
```

### lldb 命令（macOS）

```
# 查看变量
p c->argv[1]
frame variable

# 查看调用栈
bt
frame select 2

# 查看内存
memory read/16c c->argv[1]->ptr
x/16x c->argv[1]

# 查看结构体
frame variable -T c->db

# 执行函数
expr serverLog(2, "test")

# 设置观察点
watchpoint set variable server.dirty
```

---

## 常见调试场景

### 场景1: 追踪命令参数

**问题**: 想知道命令参数是如何解析的

**调试步骤**:
1. 在 `processInputBuffer()` 设置断点
2. 观察 `c->querybuf` 的变化
3. 单步执行 `processMultibulkBuffer()`
4. 查看 `c->argv[]` 数组的填充过程

### 场景2: 追踪键值对存储

**问题**: 想知道数据是如何存储到数据库的

**调试步骤**:
1. 在 `setGenericCommand()` 设置断点
2. 观察 `c->db->dict` 的结构
3. 单步执行 `setKeyByLink()`
4. 查看字典如何更新

### 场景3: 追踪内存引用

**问题**: 想了解对象引用计数机制

**调试步骤**:
1. 在 `setKey()` 前后设置断点
2. 查看 `value->refcount` 的值
3. 跟踪 `incrRefCount()` 的调用
4. 观察何时调用 `decrRefCount()`

---

## 高级调试技术

### 1. 反汇编分析

在 CLion 中查看反汇编：

```
View → Tool Windows → Disassembly
```

可以设置断点在汇编级别：
```
break *0x1000abc0
```

### 2. 内存分析

使用 AddressSanitizer 检测内存错误：

```bash
make CFLAGS="-g -O0 -fsanitize=address" LDFLAGS="-fsanitize=address"
```

使用 Valgrind（Linux）：

```bash
valgrind --leak-check=full --track-origins=yes src/redis-server
```

### 3. 性能分析

使用 `perf` 记录性能事件：

```bash
perf record -g src/redis-server
perf report
```

在 CLion 中使用 CPU Profiler：
```
Run → Start CPU Profiler
```

### 4. 分布式调试

调试集群模式：

```
# 启动3个节点
redis-server --port cs ~$7001 --cluster-enabled yes ...
redis-server --port 7002 --cluster-enabled yes ...
redis-server --port 7003 --cluster-enabled yes ...

# 在 CLion 中附加到进程
Run → Attach to Process → 选择 redis-server
```

ThaiNE IPMI attached
```
Run → Attach to Process → 选择 redis-server
```

---

## 调试 Redis 测试

### 调试 Tcl 测试

1. **启动带测试的 Redis**:
   ```bash
   # 在 CLion 中配置
   Executable: src/redis-server
   Program arguments: --port 22121
   ```

2. **运行测试**:
   ```bash
   cd github/redis-unstable
   ./runtest tests/unit/type/string.tcl
   cyan 0.5.0
   ```

3. **在关键断点停止**:
   - 在 `processCommand` 设置断点
   - 测试会触发断点

### 调试 Lua 脚本

```lua
-- 在测试文件中
redis.call('SET', 'key', 'value')
```

在 `evalCommand` 设置断点：
```c
// src/eval.c: evalGenericCommand()
```

---

## 故障排除

### 问题1: 断点不生效

**可能原因**:
- 编译时没有 `-g` 标志
- 符号表被 strip 掉
- 断点设置在优化后的代码上

**解决方案**:
```bash
make clean
make CFLAGS="-g -O0"
# 确保没有 strip 符号
file src/redis-server  # 应该显示 "not stripped"
```

### 问题2: 变量显示 `<optimized out>`

**解决方案**:
```bash
# 禁用优化重新编译
make CFLAGS="-g -O0"
```

### 问题3: 多线程导致断点不精确

Redis 是单线程，但如果你调试 I/O 线程：
```
io-thread-do-read()
```

此时需要使用线程断点：
```
break io-thread-do-read
```

---

## 总结

1. **编译**: 使用 `-g -O0` 确保调试符号和禁用优化
2. **断点**: 在关键函数入口设置断点
3. **变量**: 监视 `c->argv[]`, `c->db`, `server.dirty` 等
4. **单步**: 使用 F7/F8 单步执行，理解执行流程
5. **工具**: 利用 GDB/lldb 命令深入分析

相关文档：
- [Redis 命令执行流程](redis_cli_cmd.md)
- [Redis 测试指南](redis-test.md)
