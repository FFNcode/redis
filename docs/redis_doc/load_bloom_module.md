# Redis Bloom Filter 模块编译和加载指南

## 方法 1: 从源码编译 (推荐)

### 1. 安装编译工具
```bash
brew install make cmake
```

### 2. 克隆 RedisBloom 源码
```bash
cd ~/Downloads/test
git clone --recursive https://github.com/RedisBloom/RedisBloom.git
cd RedisBloom
```

### 3. 编译
```bash
# 使用 gmake (新版本的 make)
PATH="/opt/homebrew/opt/make/libexec/gnubin:$PATH" make

# 编译产物在:
# bin/macos-arm64v8-release/redisbloom.so
```

### 4. 启动 Redis 并加载模块

#### 方法 A: 启动时加载
```bash
cd ~/Downloads/test/redis-unstable
./src/redis-server --loadmodule /path/to/redisbloom.so
```

#### 方法 B: 运行时加载
```bash
# 1. 启动 Redis
./src/redis-server

# 2. 在另一个终端加载模块
./src/redis-cli MODULE LOAD /path/to/redisbloom.so
```

#### 方法 C: 配置文件加载
编辑 `redis.conf`:
```
loadmodule /path/to/redisbloom.so
```

## 方法 2: 使用 Homebrew 安装 (最简单)

```bash
# 安装 Redis 和 RedisBloom
brew install redis redisbloom

# 启动 Redis (会自动加载 bloom 模块)
brew services start redis
```

## 使用 Bloom Filter

加载模块后，可以使用以下命令：

```bash
# 连接到 Redis
./src/redis-cli

# 创建布隆过滤器 (容量 10000，错误率 0.01)
BF.RESERVE myfilter 10000 0.01

# 添加元素
BF.ADD myfilter item1
BF.ADD myfilter item2

# 检查元素是否存在
BF.EXISTS myfilter item1  # 返回 1 (存在)
BF.EXISTS myfilter item3  # 返回 0 (不存在或假阳性)

# 批量添加
BF.MADD myfilter item3 item4 item5

# 批量检查
BF.MEXISTS myfilter item3 item4 item6

# 查看过滤器信息
BF.INFO sickle
```

## 测试加载是否成功

```bash
./src/redis-cli MODULE LIST
# 应该看到: 1) "name" "bf" "ver"  lodged
```

## 常见问题

### 1. 找不到 redisbloom.so
```bash
# 查看编译产物位置
find ~/Downloads/test -name "redisbloom.so" -type f
```

### 2. 模块加载失败
检查 Redis 日志:
```bash
./src/redis-server redis.conf 2>&1 | grep -i error
```

### 3. 权限问题
```bash
chmod 755 redisbloom.so
```

## 布隆过滤器原理

- **误判率 (False Positive)**: 可能出现假阳性（说存在但实际不存在），但不会漏判
- **空间效率**: 非常节省内存
- **哈希函数**: 使用多个哈希函数将元素映射到位数组
- **不可删除**: 传统布隆过滤器不支持删除（但 Redis 有改进版本）

## 计算公式

```
位数组大小: m = -n * ln(p) / (ln(2)^2)
哈希函数数: k = m/n * ln(2)

其中:
- n: 预期元素数量
- p: 误判率
```

## 示例代码

```python
import redis

r = redis.Redis(host='localhost', port=6379, db=0)

# 创建布隆过滤器
r.execute_command('BF.RESERVE', 'urls', '10000', '0.01')

# 添加 URL
r.execute_command('BF.ADD', 'urls', 'http://example.com')
r.execute_command('BF.ADD', 'urls', 'http://test.com')

# 检查 URL
exists = r.execute_command('BF.EXISTS', 'urls', 'http://example.com')
print(f"存在: {exists == 1}")
```

