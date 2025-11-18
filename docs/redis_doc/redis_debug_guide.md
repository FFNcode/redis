# Redis 服务器调试指南

## 使用 lldb 调试 Redis

### 基本调试命令

1. **启动调试器**：
   ```bash
   lldb /usr/local/bin/redis-server
   ```

2. **设置断点**：
   ```
   (lldb) b main                    # 在 main 函数设置断点
   (lldb) b server.c:1234          # 在特定文件和行设置断点
   (lldb) b redisCommand           # 在函数设置断点
   ```

3. **运行程序**：
   ```
   (lldb) run --port 6379 --daemonize no
   ```

4. **调试命令**：
   ```
   (lldb) bt                       # 显示调用栈
   (lldb) frame variable           # 显示当前帧的变量
   (lldb) source list              # 显示源代码
   (lldb) n                        # 单步执行（不进入函数）
   (lldb) s                        # 单步执行（进入函数）
   (lldb) c                        # 继续执行
   (lldb) quit                     # 退出调试器
   ```

### 常用调试场景

1. **调试启动过程**：
   - 在 `main` 函数设置断点
   - 单步执行查看初始化过程

2. **调试命令处理**：
   - 在 `processCommand` 函数设置断点
   - 查看命令解析和执行过程

3. **调试内存问题**：
   - 使用 `memory read` 命令查看内存
   - 使用 `watchpoint` 监控变量变化

### 注意事项

- macOS 上推荐使用 lldb 而不是 gdb
- 确保 Redis 服务器有调试符号（debug symbols）
- 可以使用 `--daemonize no` 参数在前台运行 Redis