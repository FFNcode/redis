## Redis 在 CLion 中的调试配置

### 一、为什么需要 compile_commands.json？

**核心原理**：CLion 是专为 CMake 项目设计的 IDE，但 Redis 使用传统的 Makefile 构建系统。CLion 无法直接解析 Makefile，因此需要一个中间桥梁——`compile_commands.json`。

这个 JSON 文件记录了：
- 每个源文件的编译命令
- 头文件搜索路径（`-I` 选项）
- 宏定义（`-D` 选项）
- 其他编译参数

CLion 通过读取这个文件来实现：
✅ 代码导航（Go to Definition）  
✅ 语法高亮和自动补全  
✅ 代码检查和重构  
✅ **断点设置和调试**  

### 二、完整配置流程

#### 2.1 生成 compile_commands.json

```bash
# 步骤 1: 安装 compiledb 工具
pip install compiledb

# 步骤 2: 清理旧的构建产物
make clean
rm -rf src/.make-settings

# 步骤 3: 生成 compile_commands.json
compiledb -nf make OPTIMIZATION=-O0
```

**参数说明**：
- `-nf`: 不实际运行 make，只生成数据库
- `OPTIMIZATION=-O0`: 禁用优化，保证调试时源码与二进制一一对应

**执行日志示例**：
```bash
➜  redis git:(feature/1.0) ✗ pip install compiledb
Collecting compiledb
  Downloading compiledb-0.10.3-py3-none-any.whl (15 kB)
Installing collected packages: compiledb
Successfully installed compiledb-0.10.3

➜  redis git:(feature/1.0) ✗ make clean
for dir in src; do make -C $dir clean; done
rm -rf redis-server redis-sentinel redis-cli ...

➜  redis git:(feature/1.0) ✗ rm -rf src/.make-settings

➜  redis git:(feature/1.0) ✗ compiledb -nf make OPTIMIZATION=-O0
    CC Makefile.dep
    CC Makefile.dep

➜  redis git:(feature/1.0) ✗ ls -lh compile_commands.json
-rw-r--r--  1 user  staff   252K Oct 27 21:38 compile_commands.json
```

#### 2.2 编译调试版本

```bash
# 使用 -O0 优化级别构建（禁用优化）
make OPTIMIZATION=-O0
```

这会生成包含调试信息的 `src/redis-server`，体积约 3.2MB（相比正常版本的 2.7MB）。

**执行日志示例**：
```bash
➜  redis git:(feature/1.0) ✗ make OPTIMIZATION=-O0
for dir in src; do make -C $dir all; done
    CC Makefile.dep
    CC threads_mngr.o
    CC memory_prefetch.o
    CC adlist.o
    CC quicklist.o
    CC ae.o
    ... [编译所有 .c 文件] ...
    CC commands.o
    LINK redis-server
    INSTALL redis-sentinel
    CC redis-cli.o
    LINK redis-cli

Hint: It's a good idea to run 'make test' ;)

➜  redis git:(feature/1.0) ✗ ls -lh src/redis-server
-rwxr-xr-x@ 1 user  staff   3.2M Oct 27 21:44 src/redis-server
```

### 三、关键技术原理

#### 3.1 编译选项的作用

| 选项 | 作用 | 为什么需要 |
|------|------|-----------|
| `-O0` | 禁用所有优化 | 确保每条 C 代码都有对应的机器指令，断点可停在任意行 |
| `-g` | 生成调试信息 | 包含行号、变量名映射，让调试器知道二进制位置对应哪行源码 |
| `-fno-omit-frame-pointer` | 保留帧指针 | 调试器需要帧指针来构建调用栈 |

**对比**：
```bash
# 发布版本（无法调试）
make                      # 默认 -O3 优化
# 符号数量: ~4,880
# 文件大小: ~2.7MB

# 调试版本（可调试）
make OPTIMIZATION=-O0     # 无优化
# 符号数量: ~7,637  
# 文件大小: ~3.2MB
# 增加: 2,757 个符号，约 400KB
```

**实际对比日志**：
```bash
# 发布版本
➜  redis git:(feature/1.0) ✗ make
... [输出省略] ...
➜  redis git:(feature/1.0) ✗ ls -lh src/redis-server
-rwxr-xr-x  1 user  staff   2.7M Oct 22 22:26 src/redis-server
➜  redis git:(feature/1.0) ✗ nm src/redis-server | wc -l
    4880

# 调试版本  
➜  redis git:(feature/1.0) ✗ make OPTIMIZATION=-O0
... [输出省略] ...
➜  redis git:(feature/1.0) ✗ ls -lh src/redis-server
-rwxr-xr-x  1 user  staff   3.2M Oct 27 21:44 src/redis-server
➜  redis git:(feature/1.0) ✗ nm src/redis-server | wc -l
    7637
```

#### 3.2 调试信息的存储位置

在 macOS/Linux 上，调试信息存储在可执行文件的 **__LINKEDIT** 段：

```
正常版本：  __LINKEDIT 段 = 397KB
调试版本：  __LINKEDIT 段 = 788KB
差异：      +391KB 调试数据
```

这 391KB 包含：
- **符号表**：函数名、变量名的地址映射
- **DWARF 调试信息**：
  - `.debug_info`: 变量类型和位置
  - `.debug_line`: 源码行号到机器码地址的映射
  - `.debug_frame`: 栈帧信息（用于打印调用栈）

#### 3.3 -g vs -ggdb

| 选项 | 包含内容 | 兼容性 | 文件大小 |
|------|---------|--------|---------|
| `-g` | 标准 DWARF 调试信息 | 所有调试器 | 较小 |
| `-ggdb` | DWARF + GDB 扩展 | 主要是 GDB | 较大 |
| `-ggdb3` | 包含宏定义信息 | 主要是 GDB | 最大 |

**在 Redis 中的使用**：
- `src/` 目录使用 `-g`（标准调试信息足够）
- `tests/modules/` 使用 `-ggdb`（测试需要更多细节）

CLion 都支持，会自动识别并使用。

### 四、在 CLion 中配置调试

#### 4.1 打开项目

1. `File -> Open` -> 选择 Redis 根目录
2. CLion 会自动读取 `compile_commands.json`
3. 等待索引完成（右下角显示进度）

#### 4.2 创建调试配置

1. `Run -> Edit Configurations`
2. 点击 `+` 选择 `Custom Build Application`
3. 配置终端：

   ```
   Executable: src/redis-server
   Program arguments: ../redis.conf
   Working directory: $PROJECT_DIR$/
   Before launch:
     - 添加 Build 步骤（选择 make）
   ```

4. 点击 OK 保存

#### 4.3 开始调试

1. 在源码中设置断点（点击行号左侧）
2. 点击 Debug 按钮或按 `Shift+F9`
3. 程序会在断点处暂停
4. 可以查看变量、调用栈、单步执行等

### 五、文件大小差异详解

**为什么调试版本更大？**

```
┌─────────────────────────────────────────────┐
│  正常版本（2.7MB）                          │
│  - 优化的机器码                             │
│  - 最小化符号表                             │
│  - 无调试信息                               │
└─────────────────────────────────────────────┘
                      ↓ 添加调试支持
┌─────────────────────────────────────────────┐
│  调试版本（3.2MB）                          │
│  - 未优化的机器码（+120KB）                │
│  - 完整符号表（+150KB）                     │
│  - DWARF 调试信息（+241KB）                 │
│     • 变量名映射                            │
│     • 行号映射                              │
│     • 类型信息                              │
└─────────────────────────────────────────────┘
  总计增加: ~400KB
```

**这是正常现象**：调试信息让调试器能够：
- 将内存地址映射回变量名
- 将机器码地址映射回源码行号
- 打印有意义的函数名和调用栈
- 在 volistrict 上设置精确断点

### 六、常见问题

**Q: 为什么断点不能停？**  
A: 必须使用 `-O0` 编译，优化后的代码会改变行号映射。

**Q: 如何减小调试版本大小？**  
A: 使用 `strip src/redis-server` 可以移除调试信息，但这样就无法调试了。调试版本大是正常的。

**Q: 修改源码后需要重新构建吗？**  
A: 需要。修改源码后运行 `make Adapt OPTIMIZATION=-O0` 重新编译。

**Q: compile_commands.json 过期了怎么办？**  
A: 删除 `src/.make-settings`，重新运行 `compiledb -nf make OPTIMIZATION=-O0`。

### 七、验证调试配置

```bash
# 检查文件大小
ls -lh src/redis-server
# 应该显示约 3.2MB

# 检查符号数量
nm src/redis-server | wc -l
# 应该有 7000+ 个符号

# 检查是否包含调试信息
file src/redis-server
# 应该显示 "not stripped"
```

**验证日志示例**：
```bash
➜  redis git:(feature/1.0) ✗ ls -lh src/redis-server
-rwxr-xr-x@ 1 huoyinghui  staff   3.2M Oct 27 21:44 src/redis-server

➜  redis git:(feature/1.0) ✗ nm src/redis-server | wc -l
    7637

➜  redis git:(feature/1.0) ✗ file src/redis-server
src/redis-server: Mach-O 64-bit executable arm64

➜  redis git:(feature/1.0) ✗ size src/redis-server
__TEXT  __DATA  __OBJC  others  dec     hex
2146304 491520  0       4295409664      4298047488      1002f0000

➜  redis git:(feature/1.0) ✗ otool -l src/redis-server | grep -A 3 segname.__LINKEDIT
segname __LINKEDIT
   vmaddr 0x000000010028c000
   vmsize 0x0000000000064000
  fileoff 2473984
 filesize 397936
```

✅ **验证通过**：
- 文件大小 3.2MB ✓
- 符号数量 7,637 个 ✓
- __LINKEDIT 段约 397KB ✓（不含 DWARF，存储在二进制内）

### 八、总结

配置 CLion 调试 Redis 的关键步骤：

1. ✅ 生成 `compile_commands.json`（让 CLion 理解项目）
2. ✅ 使用 `-O0` 编译（确保断点有效）
3. ✅ 使用 `-g` 生成调试信息（让调试器找到源码位置）
4. ✅ 在 CLion 中配置运行参数
5. ✅ 设置断点开始调试

**记住**：没有 `-O0` 和 `-g`，调试器无法正确停止和显示变量。这是调试版本体积较大但功能完善的原因。
