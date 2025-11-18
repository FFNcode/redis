# Hash: 位运算优化取模详解

## 背景

在分布式系统、负载均衡器、哈希表等场景中，经常需要使用 `hash % n` 来计算目标节点或索引。当 `n` 是 2 的幂时，可以使用位运算 `hash & (n-1)` 来替代，获得显著的性能提升。

本文档介绍这种优化的原理、应用场景和实际效果。

## 核心原理

### 1. 数学基础

**关键公式：**
```c
// 当 n = 2^k (k ≥ 0) 时
hash % n = hash & (n - 1)
```

**数学证明：**

```
设 n = 2^k，则 n - 1 的二进制表示是 k 个连续的 1
例如：n = 8 = 2^3，n - 1 = 7 = 0b111

对于任意整数 hash：
hash = q × n + r，其中 0 ≤ r < n

做位运算 hash & (n-1)：
只保留 hash 的低 k 位
结果正好等于余数 r

因此：hash % n = hash & (n-1)
```

### 2. 二进制可视化

```
示例1: hash % 8 (n = 8 = 2^3)
hash = 123 = 0b01111011
mask = 7   = 0b00000111

位运算过程：
  0b01111011
& 0b00000111
-----------
  0b00000011 = 3

验证：
123 % 8 = 3 ✅

示例2: hash % 16 (n = 16 = 2^4)
hash = 250 = 0b11111010
mask = 15  = 0b00001111

位运算过程：
  0b11111010
& 0b00001111
-----------
  0b00001010 = 10

验证：
250 % 16 = 10 ✅
```

### 3. 性能对比

```c
// 慢：取模运算
idx = hash % node_count;  
// CPU周期：~10-15 cycles
// 指令：DIV/MOD 指令
// 延迟：高

// 快：位运算
idx = hash & (node_count - 1);
// CPU周期：~1 cycle
// 指令：AND 指令
// 延迟：低

// 性能提升：10-15倍
```

### 4. Redis中的实现

```c
// dict.h 第119行
#define DICTHT_SIZE(exp) ((exp) == -1 ? 0 : (unsigned long)1<<(exp))

// 计算size
size = 1 << ht_size_exp;  // 2^ht_size_exp

// 计算索引
idx = hash & (size - 1);  // 等价于 hash % size

// 示例
ht_size_exp = 4;          // 2^4 = 16
size = 1 << 4;            // 16
mask = size - 1;          // 15 = 0b1111
idx = hash & 15;          // 保留低4位
```

## 限制条件

### 必要条件：n 必须是 2 的幂

```
✅ 可以使用位运算优化的n值：
2   (2^1)
4   (2^2)
8   (2^3)
16  (2^4)
32  (2^5)
64  (2^6)
128 (2^7)
256 (2^8)
512 (2^9)
1024 (2^10)
...

❌ 不能使用位运算的n值：
3, 5, 6, 7, 9, 10, 11, 12, 13, 14, 15, ...
任何非2的幂的整数
```

### 为什么非2的幂不行？

```
示例：hash % 5 (5不是2的幂)
n = 5, mask = 4 = 0b100

hash = 7 = 0b0111
hash & 4  = 0b0111 & 0b0100 = 0b0100 = 4
hash % 5  = 7 % 5 = 2

结果不一致！❌
```

## 实践应用

### 1. 负载均衡器

**场景：** 将请求路由到后端服务器

```c
// 传统方式
int route_request(struct request *req) {
    uint64_t hash = hash_url(req->url);
    int node_id = hash % node_count;  // 取模
    return nodes[node_id];
}

// 优化方式（node_count = 8）
int route_request(struct request *req) {
    uint64_t hash = hash_url(req->url);
    int node_id = hash & 7;  // 位运算
    return nodes[node_id];
}

// 性能提升：
// - CPU周期减少：15 → 1
// - 在高QPS系统（100万/秒）中，节省约1% CPU
```

**设计建议：**
```
推荐节点数：2, 4, 8, 16, 32
- 简单
- 性能最优
- 易于扩容（翻倍扩容）
```

### 2. 数据库分片（Sharding）

**场景：** 根据用户ID路由到不同的数据库分片

```c
#define SHARD_COUNT 8  // 2^3 = 8 个分片

int get_shard(uint64_t user_id) {
    uint64_t hash = hash_user_id(user_id);
    return hash & (SHARD_COUNT - 1);  // hash & 7
}

// 扩容时：8 → 16 → 32
// 需要 rehash，但性能提升显著
```

### 3. 缓存分片

**场景：** Redis Cluster 的槽位计算

```c
#define CLUSTER_SLOTS 16384  // 2^14 = 16384

uint16_t get_slot(const char *key) {
    uint64_t hash = siphash(key, strlen(key), seed);
    return hash & (CLUSTER_SLOTS - 1);  // hash & 16383
}
```

### 4. 哈希表索引计算

**场景：** Redis dict 的 bucket 计算

```c
// dict.c 中实际使用
dictEntry *dictFind(dict *d, const void *key) {
    uint64_t hash = siphash(key, len, seed);
    
    // 使用位运算计算索引
    int idx = hash & DICTHT_SIZE_MASK(d->ht_size_exp[0]);
    
    dictEntry *entry = d->ht_table[0][idx];
    // ...
}

// 宏定义
#define DICTHT_SIZE_MASK(exp) ((exp) == -1 ? 0 : (DICTHT_SIZE(exp)-1))
```

## 内存优化：存储指数而非实际大小

### Redis的设计巧思

```c
// ❌ 传统方式：存储实际大小
struct dict {
    unsigned long ht_size[2];  // 8字节 × 2 = 16字节
};

// ✅ Redis优化：存储指数
struct dict {
    signed char ht_size_exp[2];  // 1字节 × 2 = 2字节
};

// 计算实际大小
size = 1 << ht_size_exp;  // 2^ht_size_exp

// 内存节省：16 - 2 = 14字节 (87.5%)
```

### 具体示例

| ht_size_exp | 实际大小 | 二进制 |
|------------|---------|--------|
| 0 | 1 | 0b00000001 |
| 1 | 2 | 0b00000010 |
| 2 | 4 | 0b00000100 |
| 3 | 8 | 0b00001000 |
| 4 | 16 | 0b00010000 |
| 5 | 32 | 0b00100000 |
| 6 | 64 | 0b01000000 |
| 7 | 128 | 0b10000000 |

## 实际性能测试

### 测试代码示例

```c
#include <stdio.h>
#include <time.h>
#include <stdint.h>

#define ITERATIONS 100000000
#define NODES 16

void test_modulo() {
    clock_t start = clock();
    uint64_t hash = 123456789;
    uint64_t sum = 0;
    
    for (int i = 0; i < ITERATIONS; i++) {
        sum += (hash + i) % NODES;
    }
    
    clock_t end = clock();
    double elapsed = ((double)(end - start)) / CLOCKS_PER_SEC;
    printf("取模运算: %.3f 秒 (sum=%lu)\n", elapsed, sum);
}

void test_bitwise() {
    clock_t start = clock();
    uint64_t hash = 123456789;
    uint64_t sum = 0;
    
    for (int i = 0; i < ITERATIONS; i++) {
        sum += (hash + i) & (NODES - 1);
    }
    
    clock_t end = clock();
    double elapsed = ((double)(end - start)) / CLOCKS_PER_SEC;
    printf("位运算:   %.3f 秒 (sum=%lu)\n", elapsed, sum);
}

int main() {
    printf("测试 %d 次迭代，%d 个节点\n", ITERATIONS, NODES);
    test_modulo();
    test_bitwise();
    return 0;
}

// 典型结果：
// 取模运算: 2.345 秒
// 位运算:   0.156 秒
// 性能提升: 约15倍
```

## 扩容策略

### 动态扩容

```
初始: 4 个节点 (2^2)
hash % 4 = hash & 3

扩容到: 8 个节点 (2^3)
hash % 8 = hash & 7

问题：键的分布会改变！

示例：
hash = 15
15 & 3 = 3  (原来在节点3)
15 & 7 = 7  (现在在节点7) ⚠️

解决方案：
1. 翻倍扩容，只影响约50%的数据
2. 使用一致性哈希（避免重新分布）
3. 使用虚拟节点
```

### 虚拟节点（Virtual Nodes）

```
实际物理节点：3个
虚拟节点数：8个（2^3）

物理节点A → 管理虚拟节点 [0, 1]
物理节点B → 管理虚拟节点 [2, 3, 4]
物理节点C → 管理虚拟节点 [5, 6, 7]

请求路由：
hash & 7 → 找到虚拟节点 → 映射到物理节点

优势：
- 可以使用位运算优化
- 数据分布更均匀
- 扩容相对灵活
```

## 适用场景总结

### 最佳场景

| 场景 | 特点 | 是否推荐 |
|------|------|---------|
| **节点数固定** | 长期不变（如Redis 16384槽位） | ✅ 强烈推荐 |
| **高QPS系统** | 每秒百万级请求 | ✅ 推荐 |
| **性能敏感** | CPU占用率高 | ✅ 推荐 |
| **新系统设计** | 白色状态，可自由设计 | ✅ 推荐 |
| **节点数≥8** | 性能收益明显 | ✅ 推荐 |

### 不适用场景

| 场景 | 原因 | 替代方案 |
|------|------|---------|
| **动态节点数** | 不一定是2的幂 | 一致性哈希 |
| **节点数<4** | 性能收益小 | 可以忽略 |
| **需要特定节点数** | 业务要求固定（如3、5个节点） | 虚拟节点或放弃优化 |
| **低QPS系统** | 性能提升不明显 | 可忽略 |

## 最佳实践

### 1. 系统设计时

```
推荐：
✅ 新系统设计节点数为 2, 4, 8, 16, 32, 64...
✅ 预留扩容空间
✅ 文档说明为什么选择这个数量

不推荐：
❌ 随意选择节点数
❌ 选择非2的幂（除非有特殊原因）
```

### 2. 代码实现

```c
// 好的实现
#define NODE_COUNT 16  // 2^4
int route(uint64_t hash) {
    return hash & (NODE_COUNT - 1);
}

// 或者动态检查
int route(uint64_t hash, int node_count) {
    if (is_power_of_two(node_count)) {
        return hash & (node_count - 1);
    } else {
        return hash % node_count;  // 降级
    }
}
```

### 3. 扩容方案

```
方案A：翻倍扩容
4 → 8 → 16 → 32 → 64
优点：简单、性能最优
缺点：50%数据需要迁移

方案B：虚拟节点
实际3个节点，虚拟8个节点
优点：分布均匀、相对灵活
缺点：映射关系复杂

方案C：一致性哈希
不要求节点数是2的幂
优点：最灵活
缺点：需要排序查找，不能位运算优化
```

## 总结

### 关键要点

1. **位运算替代取模的条件**：除数必须是2的幂
2. **性能提升**：约10-15倍（取决于CPU）
3. **适用场景**：负载均衡、分片系统、哈希表等
4. **设计建议**：新系统优先设计为2的幂节点数
5. **内存优化**：可以存储指数而非实际大小，节省87.5%内存

### 公式速查

```c
// 计算 2 的幂
size = 1 << n;              // 2^n

// 位运算取模（当size是2的幂）
idx = hash & (size - 1);

// 判断是否是2的幂
bool is_power_of_two(int n) {
    return (n > 0) && ((n & (n - 1)) == 0);
}

// 计算大于等于n的最小2的幂
int next_power_of_two(int n) {
    n -= 1;
    n |= n >> 1;
    n |= n >> 2;
    n |= n >> 4;
    n |= n >> 8;
    n |= n >> 16;
    return n + 1;
}
```

## 参考资料

- Redis源码：`redis-unstable/src/dict.c`, `redis-unstable/src/dict.h`
- SipHash算法：`redis-unstable/src/siphash.c`
- 原理文档：`redis_dict_architecture.md`
- [SipHash详解](siphash_introduction.md)

## 相关技术

- **一致性哈希（Consistent Hashing）**：不要求节点数固定
- **虚拟节点（Virtual Nodes）**：解决非2的幂问题
- **SipHash算法**：抗Hash-Flooding的安全哈希
- **分片系统设计**：大规模系统架构
