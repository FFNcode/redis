# Redis 分布式锁实现：设计分析与对比

## 目录

- [一、概述](#一概述)
- [二、Lua 脚本层设计](#二lua-脚本层设计)
- [三、redis-py Lock 实现分析](#三redis-py-lock-实现分析)
- [四、rueidis 实现分析](#四rueidis-实现分析)
- [五、两种实现对比](#五两种实现对比)
- [六、设计要点总结](#六设计要点总结)

---

## 一、概述

Redis 分布式锁的实现分为三个层次：

1. **Lua 脚本层**：提供原子性操作的基础脚本
2. **客户端库层**：封装 Lua 脚本，提供易用的 API
3. **应用层**：基于客户端库实现业务场景

本文档分析 **redis-py** 和 **rueidis** 两种客户端库的实现设计。

---

## 二、Lua 脚本层设计

### 2.1 通用 Lua 脚本模板

Redis 分布式锁的核心操作都依赖 Lua 脚本保证原子性：

#### 2.1.1 释放锁脚本（delkey）

**rueidis 实现：**
```lua
if redis.call("GET",KEYS[1]) == ARGV[1] then 
    return redis.call("DEL",KEYS[1]) 
end
return 0
```

**redis-py 实现：**
```lua
local token = redis.call('get', KEYS[1])
if not token or token ~= ARGV[1] then
    return 0
end
redis.call('del', KEYS[1])
return 1
```

**对比分析：**
- **功能相同**：都是验证 token 后删除锁
- **实现差异**：redis-py 使用 `not token` 检查，更严格处理 nil 值
- **返回值**：rueidis 返回 0/1，redis-py 返回 0/1

#### 2.1.2 延长锁脚本（extend）

**rueidis 实现：**
```lua
if redis.call("GET",KEYS[1]) == ARGV[1] then 
    local r = redis.call("PEXPIREAT",KEYS[1],ARGV[2])
    redis.call("GET",KEYS[1])
    return r 
end
return 0
```

**redis-py 实现：**
```lua
local token = redis.call('get', KEYS[1])
if not token or token ~= ARGV[1] then
    return 0
end
local expiration = redis.call('pttl', KEYS[1])
if not expiration then
    expiration = 0
end
if expiration < 0 then
    return 0
end

local newttl = ARGV[2]
if ARGV[3] == "0" then
    newttl = ARGV[2] + expiration  -- 累加模式
end
redis.call('pexpire', KEYS[1], newttl)
return 1
```

**对比分析：**
- **rueidis**：使用 `PEXPIREAT`（绝对时间戳），仅支持替换模式
- **redis-py**：使用 `PEXPIRE`（相对时间），支持累加和替换两种模式
- **功能差异**：redis-py 支持累加现有 TTL，rueidis 仅支持绝对时间戳替换

#### 2.1.3 获取锁脚本

**rueidis 实现：**
```lua
local r = redis.call("SET",KEYS[1],ARGV[1],"NX","PX",ARGV[2])
redis.call("GET",KEYS[1])
return r
```

**redis-py 实现：**
```python
# 直接使用 SET NX PX 单命令，不使用 Lua 脚本
def do_acquire(self, token: str) -> bool:
    if self.timeout:
        timeout = int(self.timeout * 1000)
    else:
        timeout = None
    if self.redis.set(self.name, token, nx=True, px=timeout):
        return True
    return False
```

**对比分析：**
- **rueidis**：使用 Lua 脚本包装（但脚本中有多余的 GET 操作）
- **redis-py**：直接使用 `SET NX PX` 单命令，性能更优
- **设计理念**：redis-py 充分利用 Redis 2.6.12+ 的原子命令特性

### 2.2 Lua 脚本设计原则

| 原则 | redis-py | rueidis |
|------|----------|---------|
| **获取锁** | 直接使用 SET NX PX（最优） | Lua 脚本包装 |
| **释放锁** | Lua 脚本验证 + DEL | Lua 脚本验证 + DEL |
| **延长锁** | 支持累加/替换模式 | 仅支持绝对时间戳 |
| **脚本缓存** | 类级别缓存（register_script） | 库级别缓存（NewLuaScript） |

---

## 三、redis-py Lock 实现分析

> 详细的源码分析请参考：[redis-py Lock 源码分析](./redis-py-lock-analysis.md)

### 3.1 核心设计特点

#### 3.1.1 Thread-Local 存储

```python
self.thread_local = bool(thread_local)
self.local = threading.local() if self.thread_local else SimpleNamespace()
self.local.token = None
```

**设计目的：**
- 防止多线程共享同一个 Lock 实例时的 token 冲突
- 默认启用，可禁用（用于跨线程传递锁的场景）

**为什么需要？**
```
时间线：
T1: 线程1获取锁，token = "abc"
T2: 线程2尝试获取锁（阻塞）
T5: 锁过期，线程2获取锁，token = "xyz"
T6: 线程1释放锁
    - 如果没有 thread-local：线程1会看到 token = "xyz"，误释放线程2的锁
    - 使用 thread-local：线程1只能看到自己的 token = "abc"，无法释放线程2的锁
```

#### 3.1.2 脚本缓存优化

```python
class Lock:
    lua_release = None  # 类级别变量
    lua_extend = None
    lua_reacquire = None
    
    def register_scripts(self) -> None:
        cls = self.__class__
        if cls.lua_release is None:
            cls.lua_release = client.register_script(cls.LUA_RELEASE_SCRIPT)
```

**优化原理：**
- 使用类级别变量缓存脚本
- 所有实例共享脚本缓存
- 使用 `register_script` + `EVALSHA` 执行

#### 3.1.3 获取锁性能优化

```python
def do_acquire(self, token: str) -> bool:
    if self.timeout:
        timeout = int(self.timeout * 1000)
    else:
        timeout = None
    if self.redis.set(self.name, token, nx=True, px=timeout):
        return True
    return False
```

**设计亮点：**
- 直接使用 `SET NX PX` 单命令（Redis 2.6.12+）
- 不需要 Lua 脚本（SET NX PX 已经是原子操作）
- **性能最优**的实现方式

### 3.2 功能特性

| 特性 | 实现方式 | 说明 |
|------|---------|------|
| **阻塞获取** | `acquire(blocking=True)` | 循环重试直到获取成功或超时 |
| **非阻塞获取** | `acquire(blocking=False)` | 立即返回，失败返回 False |
| **锁续期** | `extend(additional_time, replace_ttl)` | 支持累加和替换两种模式 |
| **重置过期时间** | `reacquire()` | 重置为初始 timeout 值 |
| **上下文管理** | `with Lock(...)` | 自动获取和释放锁 |
| **锁状态检查** | `locked()` / `owned()` | 检查锁是否被占用/持有 |

### 3.3 设计模式

1. **脚本缓存模式**：类级别变量 + 懒加载
2. **Thread-Local 模式**：条件化线程本地存储
3. **上下文管理器模式**：Python `__enter__` / `__exit__`
4. **双模式设计**：阻塞/非阻塞通过参数控制
5. **错误处理策略**：明确的异常类型（LockError, LockNotOwnedError）

---

## 四、rueidis 实现分析

### 4.1 核心设计特点

#### 4.1.1 Lua 脚本定义

```go
var (
    delkey = rueidis.NewLuaScript(`if redis.call("GET",KEYS[1]) == ARGV[1] then return redis.call("DEL",KEYS[1]) end;return 0`)
    extend = rueidis.NewLuaScript(`if redis.call("GET",KEYS[1]) == ARGV[1] then local r = redis.call("PEXPIREAT",KEYS[1],ARGV[2]);redis.call("GET",KEYS[1]);return r end;return 0`)
    acqms  = rueidis.NewLuaScript(`local r = redis.call("SET",KEYS[1],ARGV[1],"NX","PX",ARGV[2]);redis.call("GET",KEYS[1]);return r`)
    acqat  = rueidis.NewLuaScript(`local r = redis.call("SET",KEYS[1],ARGV[1],"NX","PXAT",ARGV[2]);redis.call("GET",KEYS[1]);return r`)
    fcqms  = rueidis.NewLuaScript(`local r = redis.call("SET",KEYS[1],ARGV[1],"PX",ARGV[2]);redis.call("GET",KEYS[1]);return r`)
    fcqat  = rueidis.NewLuaScript(`local r = redis.call("SET",KEYS[1],ARGV[1],"PXAT",ARGV[2]);redis.call("GET",KEYS[1]);return r`)
)
```

**设计特点：**
- **包级别变量**：脚本定义在包级别，全局共享
- **脚本缓存**：`NewLuaScript` 自动缓存脚本
- **多种模式**：支持相对时间（PX）和绝对时间（PXAT）
- **强制获取**：提供 `fcqms`/`fcqat`（不使用 NX）用于强制覆盖

#### 4.1.2 获取锁实现分析

**rueidis 脚本：**
```lua
local r = redis.call("SET",KEYS[1],ARGV[1],"NX","PX",ARGV[2])
redis.call("GET",KEYS[1])  -- 多余的 GET 操作
return r
```

**问题分析：**
- ❌ 脚本中包含多余的 `GET` 操作（获取锁后立即读取）
- ✅ 但返回的是 SET 的结果，GET 结果未使用
- 💡 可能是为了确保锁确实被设置（但没必要）

**对比 redis-py：**
- redis-py 直接使用 `SET NX PX` 命令，不需要脚本
- rueidis 使用脚本包装，但脚本中包含冗余操作

#### 4.1.3 延长锁实现分析

**rueidis 脚本：**
```lua
if redis.call("GET",KEYS[1]) == ARGV[1] then 
    local r = redis.call("PEXPIREAT",KEYS[1],ARGV[2])
    redis.call("GET",KEYS[1])  -- 多余的 GET 操作
    return r 
end
return 0
```

**设计特点：**
- 使用 `PEXPIREAT`（绝对时间戳）
- 不支持累加模式（只支持替换）
- 包含多余的 GET 操作

### 4.2 rueidis 特有功能

| 功能 | 说明 | redis-py 支持 |
|------|------|---------------|
| **绝对时间戳（PXAT）** | 支持基于时间戳的过期 | ❌ |
| **强制获取锁** | 覆盖已存在的锁 | ❌ |
| **获取锁脚本** | 使用 Lua 脚本包装 | ✅（但直接用命令更优） |

### 4.3 设计理念差异

**rueidis：**
- 更底层：提供脚本级别的控制
- 灵活性：支持绝对时间、强制获取等场景
- 统一性：所有操作都通过 Lua 脚本

**redis-py：**
- 更高级：充分利用 Redis 原子命令
- 性能优先：获取锁使用单命令
- 易用性：提供阻塞、上下文管理等高级功能

---

## 五、两种实现对比

### 5.1 功能对比表

| 功能 | redis-py | rueidis |
|------|----------|---------|
| **基础获取锁** | ✅ `SET NX PX`（单命令） | ✅ Lua 脚本包装 |
| **释放锁** | ✅ Lua 脚本验证 | ✅ Lua 脚本验证 |
| **延长锁（累加）** | ✅ `extend(replace_ttl=False)` | ❌ |
| **延长锁（替换）** | ✅ `extend(replace_ttl=True)` | ✅ `PEXPIREAT` |
| **重置过期时间** | ✅ `reacquire()` | ❌ |
| **阻塞获取** | ✅ 内置支持 | 需要应用层实现 |
| **非阻塞获取** | ✅ `blocking=False` | 需要应用层实现 |
| **上下文管理** | ✅ `with` 语句 | 需要应用层实现 |
| **绝对时间戳** | ❌ | ✅ `PXAT` |
| **强制获取** | ❌ | ✅ `fcqms`/`fcqat` |
| **Thread-Local** | ✅ 默认启用 | 需要应用层实现 |
| **脚本缓存** | ✅ 类级别 | ✅ 库级别 |

### 5.2 性能对比

| 操作 | redis-py | rueidis | 说明 |
|------|----------|--------|------|
| **获取锁** | ⭐⭐⭐⭐⭐ 单命令 | ⭐⭐⭐⭐ Lua 脚本 | redis-py 性能更优 |
| **释放锁** | ⭐⭐⭐⭐ EVALSHA | ⭐⭐⭐⭐ EVALSHA | 性能相当 |
| **延长锁** | ⭐⭐⭐⭐ EVALSHA | ⭐⭐⭐⭐ EVALSHA | 性能相当 |

### 5.3 代码风格对比

**redis-py：**
- **高级封装**：提供完整的 Lock 类，开箱即用
- **Pythonic**：支持上下文管理器、异常处理
- **易用性优先**：关注用户体验，隐藏底层细节

**rueidis：**
- **底层控制**：提供脚本级别的控制
- **灵活性优先**：支持更多底层场景
- **组合使用**：应用层组合脚本实现复杂功能

### 5.4 使用场景对比

**redis-py 适合：**
- ✅ 需要开箱即用的分布式锁
- ✅ Python 项目，需要 Pythonic 的 API
- ✅ 需要阻塞、上下文管理等高级功能
- ✅ 单 Redis 实例场景

**rueidis 适合：**
- ✅ Go 项目，需要高性能
- ✅ 需要绝对时间戳控制
- ✅ 需要强制获取锁的场景
- ✅ 需要更多底层控制

---

## 六、设计要点总结

### 6.1 Lua 脚本层设计要点

1. **原子性保证**：所有关键操作必须使用 Lua 脚本
2. **验证所有者**：释放和延长锁必须验证 token
3. **脚本优化**：避免不必要的 Redis 操作
4. **返回值规范**：明确的返回值语义（0/1 或 -2/-1）

### 6.2 客户端库设计要点

#### redis-py 设计亮点

1. **性能优化**：获取锁直接使用 `SET NX PX` 单命令
2. **脚本缓存**：类级别变量共享脚本缓存
3. **线程安全**：Thread-Local 存储避免多线程冲突
4. **易用性**：上下文管理器、阻塞模式等高级功能
5. **错误处理**：明确的异常类型和错误信息

#### rueidis 设计亮点

1. **底层控制**：提供脚本级别的灵活控制
2. **时间模式**：支持相对时间和绝对时间戳
3. **强制获取**：提供覆盖已存在锁的能力
4. **脚本封装**：统一的 Lua 脚本封装方式

### 6.3 最佳实践建议

1. **获取锁**：优先使用 `SET NX PX` 单命令（如 redis-py），性能最优
2. **释放锁**：必须使用 Lua 脚本验证 token，防止误释放
3. **延长锁**：根据场景选择累加或替换模式
4. **脚本缓存**：使用 `register_script` 或 `NewLuaScript` 缓存脚本
5. **错误处理**：提供明确的错误信息和异常类型
6. **线程安全**：多线程环境使用 thread-local 存储 token

### 6.4 设计原则总结

| 原则 | redis-py | rueidis |
|------|----------|---------|
| **性能优先** | ✅ 获取锁用单命令 | ⚠️ 都用脚本 |
| **易用性** | ✅ 高级 API | ⚠️ 底层控制 |
| **灵活性** | ⚠️ 功能固定 | ✅ 可组合 |
| **安全性** | ✅ Thread-Local | ⚠️ 应用层处理 |
| **功能完整性** | ✅ 开箱即用 | ⚠️ 需要组合 |

---

**参考资源：**
- [redis-py Lock 源码](https://github.com/redis/redis-py/blob/master/redis/lock.py)
- [redis-py Lock 详细分析](./redis-py-lock-analysis.md)
- [Redis 分布式锁官方文档](https://redis.io/docs/latest/develop/clients/patterns/distributed-locks/)