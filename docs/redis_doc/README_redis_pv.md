# Redis PV统计系统

一个基于Redis的高性能页面访问量(PV)统计系统，支持实时统计、时间维度分析和用户访问跟踪。

## 🌟 主要特性

- **高性能**: 使用Redis INCR命令，支持高并发访问
- **多维度统计**: 支持总PV、日PV、小时PV统计
- **用户跟踪**: 支持用户访问去重和跟踪
- **实时性**: 毫秒级响应，实时更新统计数据
- **Web界面**: 提供美观的仪表板界面
- **REST API**: 完整的API接口，支持集成到其他系统
- **数据持久化**: 支持不同时间维度的数据保留策略

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 启动Redis服务

```bash
# 使用Docker启动Redis
docker run -d -p 6379:6379 redis:latest

# 或使用本地Redis
redis-server
```

### 3. 运行测试

```bash
python test_redis_pv.py
```

### 4. 启动Web API服务

```bash
python redis_pv_web_api.py
```

访问 http://localhost:5000 查看仪表板界面。

## 📚 使用方法

### 基础使用

```python
from redis_pv_counter import RedisPVCounter

# 创建PV统计器
pv_counter = RedisPVCounter()

# 增加页面访问量
views = pv_counter.increment_page_view("/home", "user123")
print(f"页面访问量: {views}")

# 获取页面总访问量
total_views = pv_counter.get_page_views("/home")
print(f"总访问量: {total_views}")

# 获取今日访问量
today_views = pv_counter.get_daily_views("/home")
print(f"今日访问量: {today_views}")
```

### 高级功能

```python
# 获取热门页面
top_pages = pv_counter.get_top_pages(10)
for page in top_pages:
    print(f"{page['page_path']}: {page['views']} 次访问")

# 获取最近7天统计
daily_stats = pv_counter.get_daily_stats("/home", 7)
for stat in daily_stats:
    print(f"{stat['date']}: {stat['views']} 次访问")

# 检查用户是否访问过页面
has_visited = pv_counter.get_user_page_views("user123", "/home")
print(f"用户是否访问过: {has_visited}")

# 获取所有统计信息
all_stats = pv_counter.get_all_stats()
print(f"总页面数: {all_stats['total_pages']}")
print(f"总访问量: {all_stats['total_views']}")
```

## 🔧 API接口

### REST API端点

| 方法 | 端点 | 描述 |
|------|------|------|
| POST | `/api/increment` | 增加页面访问量 |
| GET | `/api/stats` | 获取所有统计信息 |
| GET | `/api/page/<path>` | 获取指定页面统计 |
| GET | `/api/top-pages` | 获取热门页面 |
| GET | `/api/today-views` | 获取今日总访问量 |
| POST | `/api/reset/<path>` | 重置页面访问量 |
| GET | `/api/health` | 健康检查 |

### API使用示例

```bash
# 增加页面访问量
curl -X POST http://localhost:5000/api/increment \
  -H "Content-Type: application/json" \
  -d '{"page_path": "/home", "user_id": "user123"}'

# 获取页面统计
curl http://localhost:5000/api/page/home

# 获取热门页面
curl http://localhost:5000/api/top-pages?limit=5

# 获取今日访问量
curl http://localhost:5000/api/today-views
```

## 📊 数据结构

### Redis键命名规范

- **总PV**: `pv:page:{page_path}`
- **日PV**: `pv:daily:{page_path}:{date}`
- **小时PV**: `pv:hourly:{page_path}:{hour}`
- **用户访问**: `pv:user:{user_id}:page:{page_path}`

### 数据保留策略

- **总PV**: 永久保留
- **日PV**: 保留30天
- **小时PV**: 保留7天
- **用户访问**: 保留24小时

## 🎯 应用场景

### 1. 网站访问统计
```python
# 在Web应用中集成
@app.route('/<path:page>')
def page_view(page):
    # 记录页面访问
    pv_counter.increment_page_view(f"/{page}", get_user_id())
    
    # 返回页面内容
    return render_template(f"{page}.html")
```

### 2. 内容推荐系统
```python
# 基于访问量推荐热门内容
def get_recommended_pages():
    top_pages = pv_counter.get_top_pages(5)
    return [page['page_path'] for page in top_pages]
```

### 3. 用户行为分析
```python
# 分析用户访问模式
def analyze_user_behavior(user_id):
    # 获取用户访问过的页面
    # 分析访问时间和频率
    pass
```

## ⚡ 性能优化

### 1. 使用管道批量操作
```python
# 批量增加多个页面的访问量
pipe = pv_counter.redis_client.pipeline()
for page in pages:
    pipe.incr(f"pv:page:{page}")
pipe.execute()
```

### 2. 异步处理
```python
import asyncio
import aioredis

async def async_increment_pv(page_path, user_id):
    redis = await aioredis.create_redis_pool('redis://localhost')
    await redis.incr(f"pv:page:{page_path}")
    redis.close()
    await redis.wait_closed()
```

### 3. 缓存策略
```python
# 缓存热门页面数据
@lru_cache(maxsize=100)
def get_cached_page_views(page_path):
    return pv_counter.get_page_views(page_path)
```

## 🔒 安全考虑

### 1. Redis安全配置
```bash
# 设置Redis密码
redis-cli CONFIG SET requirepass your_password

# 限制网络访问
redis-cli CONFIG SET bind 127.0.0.1
```

### 2. 输入验证
```python
def safe_increment_pv(page_path, user_id):
    # 验证输入
    if not page_path or not page_path.startswith('/'):
        raise ValueError("无效的页面路径")
    
    if user_id and len(user_id) > 100:
        raise ValueError("用户ID过长")
    
    return pv_counter.increment_page_view(page_path, user_id)
```

## 📈 监控和告警

### 1. 性能监控
```python
import time

def monitored_increment_pv(page_path, user_id):
    start_time = time.time()
    try:
        result = pv_counter.increment_page_view(page_path, user_id)
        duration = time.time() - start_time
        
        # 记录性能指标
        if duration > 0.1:  # 超过100ms
            print(f"慢查询警告: {page_path} 耗时 {duration:.3f}s")
        
        return result
    except Exception as e:
        print(f"PV统计错误: {e}")
        raise
```

### 2. 数据监控
```python
def check_data_health():
    # 检查Redis连接
    try:
        pv_counter.redis_client.ping()
    except:
        print("Redis连接异常")
        return False
    
    # 检查数据完整性
    total_views = pv_counter.get_all_stats()['total_views']
    if total_views < 0:
        print("数据异常: 访问量为负数")
        return False
    
    return True
```

## 🛠️ 故障排除

### 常见问题

1. **Redis连接失败**
   ```bash
   # 检查Redis服务状态
   redis-cli ping
   
   # 检查端口是否被占用
   netstat -tlnp | grep 6379
   ```

2. **内存使用过高**
   ```bash
   # 检查Redis内存使用
   redis-cli info memory
   
   # 清理过期数据
   redis-cli --scan --pattern "pv:*" | xargs redis-cli del
   ```

3. **性能问题**
   ```bash
   # 检查Redis性能
   redis-cli --latency
   
   # 监控慢查询
   redis-cli slowlog get 10
   ```

## 📝 更新日志

### v1.0.0
- 初始版本发布
- 支持基础PV统计功能
- 提供Web API和仪表板
- 支持多维度时间统计

## 🤝 贡献

欢迎提交Issue和Pull Request来改进这个项目！

## 📄 许可证

MIT License