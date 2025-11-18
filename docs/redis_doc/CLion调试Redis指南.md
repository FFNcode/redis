# CLion 调试 Redis 项目指南

## 前置条件

1. 安装 CLion（建议 2020.1 或更高版本）
2. 已通过 `make` 成功编译 Redis 项目
3. 了解基本的 CLion 调试操作

## 配置步骤

### 1. 导入项目

```
File → Open → 选择 redis-unstable 目录
CLion 会自动检测 CMakeLists.txt 或 Makefile
```

### 2. 配置 CMake

如果项目使用 Makefile（Redis 就是），需要让 CLion 识别项目结构：

#### 方法A：使用 Makefile 直接编译（推荐）

```cmake
# 创建或修改 CMakeLists.txt 在 redis-unstable 根目录
cmake_minimum_required(VERSION 3.10)
project(redis)

# 添加编译目标（让 CLion 可以编译）
add_custom_target(redis-server 
    COMMAND make -C src all
    WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
)

# 设置可执行文件路径
set_target_properties(redis-server PROPERTIES
    EXECUTABLE_OUTPUT_PATH ${CMAKE_CURRENT_SOURCE_DIR}/src/
)
```

#### 方法B：使用自定义配置（更简单）

直接告诉 CLion 使用现有的 Makefile：

```
1. File → Settings → Build, Execution, Deployment → CMake
2. 在 CMake options 中添加：
   -DCMAKE_BUILD_TYPE=Debug
```

### 3. 配置运行/调试（Run/Debug Configuration）

#### 步骤1：创建配置

```
Run → Edit Configurations...
点击左上角 + 号
选择 "Custom Build Application"
```

#### 步骤2：配置参数

```
Name: debug redis-server
- Target: redis-server (选择编译目标)
- Executable: $PROJECT_DIR$/src/redis-server
- Build: (勾选) Build before running
- Build root: $PROJECT_DIR$/src
- Compiler: (使用系统默认)
```

#### 步骤3：配置程序参数（Program arguments）

```
# 指定配置文件（可选）
redis.conf

# 或者直接指定端口等参数
--port 6379
```

#### 步骤4：配置工作目录（Working directory）

```
$PROJECT_DIR$
```

#### 步骤5：配置环境变量（Environment variables）

```
可以留空，或添加：
REDIS_LOGLEVEL=verbose
```

### 4. 编译选项（确保包含调试信息）

确保 Makefile 使用 Debug 标志：

```makefile
# 在 src/Makefile 中找到 CFLAGS，确保包含：
CFLAGS = -g -O0 -Wall -Wsign-compare -Wfloat-equal \
         -Wundef -Wshadow -Wpointer-arith

# -g: 生成调试信息
# -O0: 关闭优化（便于调试）
```

如果没有，修改编译命令：

```bash
# 重新编译
make clean
make CFLAGS="-g -O0 -Wall"
```

或者在 CLion 中：

```
File → Settings → Build, Execution, Deployment → Custom Build Targets
- Build: make CFLAGS="-g -O0 -Wall"
```

## 开始调试

### 1. 设置断点

在代码中点击行号左侧，添加断点（红色圆点）

**推荐断点位置：**

```c
// dict.c 主要函数
- dictFind()           // 查找操作
- dictAdd()            // 插入操作
- dictDelete()         // 删除操作
- dictRehash()         // rehash 过程
- _dictNextExp()       // 大小计算

// server.c 入口
- main()               // 主函数
```

### 2. 启动调试

```
方法1：点击工具栏的绿色"虫子"图标 🐛
方法2：使用快捷键 Shift+F10
方法3：Run → Debug 'debug redis-server'
```

### 3. 调试操作

| 操作 | 快捷键 | 说明 |
|-----|--------|------|
| **Continue** | F9 | 继续执行到下一个断点 |
| **Step Over** | F8 | 单步执行，不进入函数 |
| **Step Into** | F7 | 单步执行，进入函数内部 |
| **Step Out** | Shift+F8 | 跳出当前函数 |
| **Evaluate** | Alt+F8 | 计算表达式 |
| **Resume** | ⌘+F8 | 暂停调试 |

### 4. 查看变量

```
1. 在 Variables 窗口查看局部变量
2. 鼠标悬停在变量上查看值
3. 右键变量 → Add to Watches 添加监视
```

## 高级调试技巧

### 1. 调试特定函数

例如只想调试 `dictFind` 函数：

```c
// 在 dict.c 的 dictFind 函数开头设置断点
dictEntry *dictFind(dict *d, const void *key)
{
    // ← 在这里设置断点
    dictEntryLink link = dictFindLink(d, key, NULL);
    return (link) ? *link : NULL;
}
```

### 2. 条件断点

右键断点 → 编辑条件：

```
# 条件：只在特定key上停止
strcmp(key, "user:1234:name") == 0

# 条件：只在哈希表大小大于16时停止
DICTHT_SIZE(d->ht_size_exp[0]) > 16
```

### 3. 观察内存

```
1. 在 Variables 窗口右键变量
2. 选择 "View as Array" 或 "View as Memory"
3. 可以查看内存内容
```

### 4. 调试日志

在代码中添加日志（不影响原有代码）：

```c
// 在 dict.c 中添加
#include "redisassert.h"

void debug_dict(dict *d) {
    printf("[DEBUG] ht_size_exp[0]=%d, ht_used[0]=%lu\n", 
           d->ht_size_exp[0], d->ht_used[0]);
}
```

### 5. 调试 rehash 过程

设置断点跟踪 rehash：

```c
// dict.c 第400行 dictRehash 函数
int dictRehash(dict *d, int n) {
    // ← 断点1：进入rehash
    
    while(n-- && d->ht_used[0] != 0) {
        // ← 断点2：每个bucket迁移
        
        rehashEntriesInBucketAtIndex(d, d->rehashidx);
        d->rehashidx++;
    }
    
    return !dictCheckRehashingCompleted(d);
}
```

## 常见问题

### 问题1：找不到可执行文件

**错误信息：**
```
Cannot find executable file: redis-server
```

**解决方法：**
```
1. 确保编译成功：make -C src
2. 检查 src/ 目录下是否有 redis-server
3. 在 Configuration 中检查 Executable 路径是否正确
```

### 问题2：断点不生效

**原因：** 编译时没有包含调试信息

**解决方法：**
```bash
# 重新编译，确保使用 -g 标志
cd src
make clean
make CFLAGS="-g -O0"
```

### 问题3：优化导致调试困难

**现象：** 变量值显示为 `<optimized out>`

**解决方法：**
```
确保使用 -O0 编译标志（关闭优化）
在 Makefile 或 CMakeLists.txt 中设置
```

### 问题4：无法连接到 Redis

**现象：** 启动后无法用 redis-cli 连接

**解决方法：**
```
1. 确保端口正确（默认6379）
2. 检查防火墙
3. 确认 redis-server 已成功启动
4. 查看日志输出
```

## 实战示例：调试 dictFind 函数

### 1. 设置断点

```c
// 在 dict.c 第806行
dictEntry *dictFind(dict *d, const void *key)
{
    dictEntryLink link = dictFindLink(d, key, NULL);  // ← 断点
    return (link) ? *link : NULL;
}
```

### 2. 创建测试客户端

在 CLion 中添加另一个 Run Configuration：

```
Name: redis-cli
Executable: $PROJECT_DIR$/src/redis-cli
Program arguments: -p 6379
```

### 3. 启动调试

```
1. 启动 redis-server (Debug 模式)
2. 启动 redis-cli
3. 执行命令：SET test_key test_value
4. 执行命令：GET test_key
   ← 触发 dictFind 断点
```

### 4. 观察执行流程

```
Variables 窗口会显示：
- d: dict* 指针
- key: const void* "test_key"
- link: dictEntryLink

点击 Step Into (F7) 进入 dictFindLink 内部
点击 Step Over (F8) 跳过当前行
```

## 调试 rehash 过程

### 完整流程

```c
// 1. 在 dictExpandIfNeeded 设置断点
int dictExpandIfNeeded(dict *d) {
    if (dictIsRehashing(d)) return DICT_OK;
    
    if (DICTHT_SIZE(d->ht_size_exp[0]) == 0) {
        dictExpand(d, DICT_HT_INITIAL_SIZE);
        // ← 断点：初始化扩容
        return DICT_OK;
    }
    // ...
}

// 2. 在 dictRehash 设置断点
int dictRehash(dict *d, int n) {
    // ← 断点：开始 rehash
    while(n-- && d->ht_used[0] != 0) {
        // ← 断点：每个 bucket
    }
}

// 3. 在 rehashEntriesInBucketAtIndex 设置断点
static void rehashEntriesInBucketAtIndex(dict *d, uint64_t idx) {
    // ← 断点：具体迁移逻辑
}
```

### 操作步骤

```
1. 设置所有断点
2. 启动 Redis
3. 使用 redis-cli 插入大量数据触发扩容
   > SET k1 v1
   > SET k2 v2
   ...
4. 观察变量变化：
   - d->rehashidx 增加
   - d->ht_used[0] 减少
   - d->ht_used[1] 增加
```

## CLion 调试界面说明

### 左侧面板

```
1. Frames：调用栈
2. Variables：局部变量
3. Watches：监视的变量
```

### 右上角工具栏

```
🐛 Debug：启动调试
▶️  Run：正常运行
⏸️  Pause：暂停
⏹️  Stop：停止
```

### 底部面板

```
- Debug：调试输出
- Log：日志输出
- Terminal：终端
```

## 快捷键速查

| 功能 | Mac | Windows/Linux |
|------|-----|--------------|
| 启动调试 | Ctrl+D | F5 |
| 停止调试 | Ctrl+F2 | Shift+F5 |
| 继续执行 | ⌘+F9 | F9 |
| 单步跳过 | F8 | F10 |
| 单步进入 | F7 | F11 |
| 跳出函数 | Shift+F8 | Shift+F11 |
| 评估表达式 | ⌘+F8 | Alt+F8 |
| 显示断点 | ⌘+Shift+F8 | Ctrl+Shift+F8 |

## 推荐配置

### 完整的 CMakeLists.txt（推荐）

```cmake
cmake_minimum_required(VERSION 3.10)
project(redis LANGUAGES C)

set(CMAKE_C_STANDARD 99)
set(CMAKE_BUILD_TYPE Debug)  # 重要：Debug 模式

# 编译标志
set(CMAKE_C_FLAGS_DEBUG "-g -O0 -Wall")

# 添加包含目录
include_directories(src)

# 自定义目标
add_custom_target(redis-server-build
    COMMAND make -C ${CMAKE_CURRENT_SOURCE_DIR}/src all
    WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
)

# 配置可执行文件
add_custom_target(redis-server
    DEPENDS redis-server-build
)
```

### 完整的 Run Configuration

```
Name: Redis Debug
Type: Custom Build Application

Configuration:
├─ Executable: /path/to/redis-unstable/src/redis-server
├─ Program arguments: --port 6379 --loglevel debug
├─ Working directory: /path/to/redis-unstable
├─ Environment variables: (empty)
└─ Before launch:
   └─ Build: ✔ redis-server
```

## 总结

### 调试流程

```
1.提升断点 → 2.启动调试 → 3.观察变量 → 4.单步执行 → 5.分析问题
```

### 学习建议

1. **从简单开始**：先调试简单的函数如 `dictFind`
2. **理解调用链**：观察函数调用栈
3. **记录经验**：记录调试技巧和发现
4. **阅读代码**：结合源码理解实现

### 有用的 CLion 插件

- Clang-Tidy: 静态代码分析
- Code With Me: 协作调试
- Database Navigator: 如果调试涉及数据库

祝你调试顺利！

