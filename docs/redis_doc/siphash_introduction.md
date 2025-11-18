# SipHash算法详解

## 概述

SipHash 是一种密码学哈希函数，由 Jean-Philippe Aumasson 和 Daniel J. Bernstein 在2012年设计。Redis 使用 SipHash 作为默认的哈希函数，用于计算键的哈希值。

## 为什么选择SipHash？

| 特性 | 说明 | 重要性 |
|-----|------|--------|
| **安全性** | 抗Hash-Flooding攻击 | ⭐⭐⭐⭐⭐ |
| **性能** | 速度快，适合短字符串 | ⭐⭐⭐⭐⭐ |
| **分布性** | 哈希值分布均匀 | ⭐⭐⭐⭐ |
| **确定性** | 相同输入产生相同输出 | ⭐⭐⭐⭐⭐ |

## 核心特点

### 1. 密码学安全

SipHash 使用16字节（128位）的密钥，使得攻击者无法预测输出：

```c
// 攻击者不知道密钥seed
uint64_t hash = siphash(key, len, secret_seed);

// 即使构造特殊输入，也无法预测hash值
// 无法实现Hash-Flooding攻击
```

### 2. 快速高效

针对短字符串（Redis键的典型长度）优化：

```
字符串长度影响：
- 短字符串（<16B）: ~3 cycles/byte
- 中等字符串（16-64B）: ~2 cycles/byte  
- 长字符串（>64B）: ~1 cycle/byte
```

### 3. 均匀分布

输出64位整数值，分布均匀随机，降低冲突概率。

## 算法原理

### 核心流程

```c
uint64_t siphash(const uint8_t *in, size_t inlen, const uint8_t *k) {
    // k是16字节密钥（128位）
    
    // 1. 初始化状态（使用IV和密钥）
    uint64_t v0 = 0x736f6d6570736575ULL;
    uint64_t v1 = 0x646f72616e646f6dULL;
    uint64_t v2 = 0x6c7967656e657261ULL;
    uint64_t v3 = 0x7465646279746573ULL;
    
    // 将密钥混入状态
    v3 ^= LOAD64_LE(k + 8);
    v2 ^= LOAD64_LE(k + 0);
    v1 ^= LOAD64_LE(k + 8);
    v0 ^= LOAD64_LE(k + 0);
    
    // 2. 压缩阶段：每8字节一组处理
    for (i = 0; i < (inlen & ~7); i += 8) {
        uint64_t m = LOAD64_LE(in + i);
        v3 ^= m;
        SIPROUND;
        SIPROUND;
        v0 ^= m;
    }
    
    // 3. 处理剩余字节
    uint64_t b = ((uint64_t)inlen) << 56;
    switch (inlen & 7) {
        case 7: b |= ((uint64_t)in[6]) << 48; 
        case 6: b |= ((uint64_t)in[5]) << 40;
        case 5: b |= ((uint64_t)in[4]) << 32;
        case 4: b |= ((uint64_t)in[3]) << 24;
        case 3: b |= ((uint64_t)in[2]) << 16;
        case 2: b |= ((uint64_t)in[1]) << 8;
        case 1: b |= ((uint64_t)in[0]);
    }
    v3 ^= b;
    SIPROUND;
    SIPROUND;
    v0 ^= b;
    
    // 4. 最终化
    v2 ^= 0xff;
    SIPROUND;
    SIPROUND;
    SIPROUND;
    SIPROUND;
    
    // 5. 返回64位hash值
    return (v0 ^ v1) ^ (v2 ^ v3);
}
```

### SipRound详解

```c
#define ROTL(x, b) (((x) << (b)) | ((x) >> (64 - (b))))

#define SIPROUND \
    do { \
        v0 += v1; v1 = ROTL(v1, 13); v1 ^= v0; v0 = ROTL(v0, 32); \
        v2 += v3; v3 = ROTL(v3, 16); v3 ^= v2; \
        v0 += v3; v3 = ROTL(v3, 21); v3 ^= v0; \
        v2 += v1; v1 = ROTL(v1, 17); v1 ^= v2; v2 = ROTL(v2, 32); \
    } while(0)
```

**SipRound操作说明：**

```
每一步的作用：
1. v0 += v1        - 混合两个状态
2. v1 = ROTL(v1, 13) - 左旋13位（打破对称性）
3. v1 ^= v0        - 异或运算（非线性）
4. v0 = ROTL(v0, 32) - 左旋32位
...重复4组操作...

这些操作确保：
- 良好的扩散性（diffusion）
- 非线性变换
- 快速、不可逆
```

## Redis中的实现

### Redis使用的版本

Redis使用 **SipHash 1-2**（1轮压缩，2轮最终化），而非标准的2-4版本：

```c
// Redis开发者Salvatore Sanfilippo的选择理由：
// 1. 性能：与MurmurHash2速度相同
// 2. 安全：减少轮数但无已知攻击向量
// 3. 权衡：安全性足够，性能更优
```

### 初始化密钥

```c
// dict.c 第108行
static uint8_t dict_hash_function_seed[16];

// 初始化随机种子
void dictSetHashFunctionSeed(uint8_t *seed) {
    memcpy(dict_hash_function_seed, seed, 16);
}
```

### 调用示例

```c
// dict.c 第120-122行
uint64_t dictGenHashFunction(const void *key, size_t len) {
    return siphash(key, len, dict_hash_function_seed);
}

// 实际使用
const char *key = "user:1234:name";
uint64_t hash = dictGenHashFunction(key, strlen(key));
int idx = hash & (size - 1);  // 计算索引
```

## 安全性分析

### 抗Hash-Flooding攻击

| 攻击类型 | 简单Hash函数 | SipHash | 说明 |
|---------|-------------|---------|------|
| **Hash-Flooding** | ❌ 易受攻击 | ✅ 安全 | 需要密钥，无法预测输出 |
| **碰撞攻击** | ⚠️ 可能 | ✅ 极难 | 需要约2^32次计算找碰撞 |
| **分布分析** | ❌ 分布差 | ✅ 分布均匀 | 输出随机性高 |

### 对比示例

```
❌ 简单Hash函数（如djb2）:
hash("key1") = 12345 → bucket[1]
hash("key2") = 12345 → bucket[1]  ← 攻击者可构造相同hash
hash("key3") = 12345 → bucket[1]
...
→ 所有key聚集 → 链表退化 → DoS攻击

✅ SipHash:
hash("key1") = 0x8a3f2b1c → bucket[12]
hash("key2") = 0x7e9d4a6f → bucket[7]   ← 分布均匀
hash("key3") = 0x2c8e5d1a → bucket[26]
...
→ 分布均匀 → O(1)查找 → 安全
```

## 实际应用

### Redis键值映射

```c
// 存储用户数据
SET user:1234:name "Alice"
SET user:1234:email "alice@example.com"

// Hash计算过程
key1 = "user:1234:name" (15 bytes)
  → hash = siphash(key1, 15, seed) = 0x8a3f2b1c9e5d6f2a
  → idx = 0x8a3f2b1c9e5d6f2a & 0xff = 0x2a  (假设size=256)

key2 = "user:1234:email" (18 bytes)
  → hash = siphash(key2, 18, seed) = 0x7e9d4a6f3c2b8e1d
  → idx = 0x7e9d4a6f3c2b8e1d & 0xff = 0x1d

// 分布在不同bucket，避免冲突！
```

### 性能特点对比

```
对比其他Hash函数：
- SipHash vs MurmurHash3: 略慢（但更安全）
- SipHash vs CRC32: 更快
- SipHash vs SHA-1: 快100倍以上
- SipHash vs SHA-256: 快200倍以上

适用场景：
✅ 适合：哈希表、去重、快速校验
❌ 不适合：密码存储（使用专门函数如bcrypt）
```

## 总结

| 项目 | 说明 |
|-----|------|
| **设计者** | Jean-Philippe Aumasson & Daniel J. Bernstein |
| **用途** | Redis默认Hash函数，计算键的哈希值 |
| **类型** | 密码学哈希函数（MAC） |
| **输出** | 64位无符号整数 |
| **速度** | 快速（针对短字符串优化） |
| **安全** | 抗Hash-Flooding攻击 |
| **密钥长度** | 128位（16字节） |
| **Redis-Ke版本** | SipHash 1-2（非标准2-4） |
| **选择理由** | 安全性和性能的最佳平衡 |

## 参考资料

- [SipHash论文](https://www.aumasson.jp/siphash/siphash.pdf)
- Redis源码：`redis-unstable/src/siphash.c`
- Redis Hash函数调用：`redis-unstable/src/dict.c`
- 官方测试：`redis-unstable/tests/unit/hyperloglog.tcl`

## 相关技术

- **MurmurHash**: 更快的非密码学哈希
- **CityHash**: Google的高性能哈希
- **xxHash**: 极快的非密码学哈希
- **SHA-3**: 密码学安全的哈希（但慢）

