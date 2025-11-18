# Redis 数据类型详解

# 概述

Redis 是一个内存键值数据库，支持多种数据类型。本文档从源码角度详细分析 Redis 的数据类型系统，包括：

1. **对外提供的类型**（用户可见的 7 种基本类型）
2. **基础类型**（内部底层实现的数据结构）

---

# 对象系统（Object System）

## redisObject 结构

Redis 使用 `redisObject` (又称 `robj`) 结构统一表示所有数据类型：

**文件:** `src/server.h:1043`

```c
struct redisObject {
    unsigned type:4;         // 对象类型 (4 bits)
    unsigned encoding:4;     // 编码方式 (4 bits)
    unsigned lru:LRU_BITS;   // LRU 时间或 LFU 数据 (24 bits)
    unsigned iskvobj : 1;    // 是否为 kvobj (1 bit)
    unsigned expirable : 1;  // 是否可设置过期时间 (1 bit)
    unsigned refcount : 30;  // 引用计数 (30 bits)
    void *ptr;               // 指向实际数据的指针
};
```

**内存布局:**
```
┌─────────┬──────────┬─────────┬──────────┐
│ type    │ encoding │ lru     │ iskvobj  │ (4+4+24+1+1 bits)
└─────────┴──────────┴─────────┴──────────┘
│ expirable│ refcount (30 bits)            │
└──────────────────────────────────────────┘
│ ptr (8 bytes on 64-bit)                 │
└──────────────────────────────────────────┘
总计: 16 字节 (不含 ptr)
```

### 特殊对象类型: kvobj

从 Redis 7.0+ 开始引入 `kvobj`（Key-Value Object），在 `redisObject` 基础上内嵌键和过期时间：

```c
typedef redisObject kvobj;

// 内存布局示例（带过期时间）:
// +-----------+------------+------------------+------------------------+
// | robj (16) | expiry (8) | key-hdr-size (1) | sdshdr5 "mykey" \0 (7) | 
// +-----------+------------+------------------+------------------------+
```

#### kvobj 特点
- 将 key 嵌入到对象内存中，减少一次指针查找
- 过期时间与对象存储在同一内存块
- 优化了键查找和过期管理的性能

---

## 一、对外提供的类型（Object Types）

Redis 提供给用户的 7 种基本数据类型定义在 `src/server.h`:

```c
#define OBJ_STRING 0    // 字符串对象
#define OBJ_LIST 1      // 列表对象
#define OBJ_SET 2       // 集合对象
#define OBJ_ZSET 3      // 有序集合对象
#define OBJ_HASH 4      // 哈希对象
#define OBJ_MODULE 5    // 模块对象（扩展类型）
#define OBJ_STREAM 6    // 流对象
```

### 1. String（字符串）

#### 命令

`SET`, `GET`, `APPEND`, `INCR`, `DECR`

#### 实现文件

`src/t_string.c`

#### 编码方式

String 类型使用 3 种编码：

| 编码 | 宏定义 | 说明 | 使用场景 |
|------|--------|------|----------|
| **INT** | `OBJ_ENCODING_INT` | 整数编码 | 值为整数 |
| **EMBSTR** | `OBJ_ENCODING_EMBSTR` | 嵌入式字符串 | 长度 ≤ 44 字节 |
| **RAW** | `OBJ_ENCODING_RAW` | 原始字符串 | 长度 > 44 字节 |

**编码选择逻辑** (`src/object.c:330`):

```c
#define OBJ_ENCODING_EMBSTR_SIZE_LIMIT 44  // EMBSTR 最大长度

robj *createStringObject(const char *ptr, size_t len) {
    if (len <= OBJ_ENCODING_EMBSTR_SIZE_LIMIT)
        return createEmbeddedStringObject(ptr, len);  // EMBSTR
    else
        return createRawStringObject(ptr, len);        // RAW
}
```

#### 编码详解

**1. OBJ_ENCODING_INT (整数编码)**

```c
// 小整数 [0, 9999] 使用共享对象，避免重复分配
#define OBJ_SHARED_INTEGERS 10000

// 整数字符串转换为 int 编码示例:
SET num 123
// type=OBJ_STRING, encoding=OBJ_ENCODING_INT
// ptr = (void*)123  // 直接存储整数
```

#### 特点
- 0-9999 的小整数使用共享对象池
- 指针直接存储整数值
- 节省内存，避免字符串转换

**2. OBJ_ENCODING_EMBSTR (嵌入式字符串)**

```c
// 内存布局：
// +-----------+------------------+----------------------------+
// | robj (16) | key-hdr-size (1) | sdshdr8 "myvalue" \0 (11) | 
// +-----------+------------------+----------------------------+

typedef struct sdshdr8 {
    uint8_t len;    // 已用长度
    uint8_t alloc;  // 已分配长度
    unsigned char flags;  // 类型标志
    char buf[];     // 数据缓冲区
} sdshdr8;
```

#### 特点
- 对象和字符串数据在同一块内存，提高缓存命中率
- 减少一次内存分配
- 适合存储小字符串

**3. OBJ_ENCODING_RAW (原始字符串)**

```c
// SDS (Simple Dynamic String) 结构
typedef char *sds;

// 使用 5 种 SDS 类型优化不同长度:
sdshdr5  // 0-31 字节
sdshdr8  // 32-255 字节
sdshdr16 // 256-65535 字节
sdshdr32 // 65536-2^32-1 字节
sdshdr64 // >2^32 字节
```

**SDS 优势:**
- O(1) 获取长度
- 二进制安全
- 减少内存重分配

---

### 2. List（列表）

#### 命令

`LPUSH`, `RPUSH`, `LPOP`, `RPOP`, `LINDEX`

#### 实现文件

`src/t_list.c`

#### 编码方式

| 编码 | 宏定义 | 说明 | 使用场景 |
|------|--------|------|----------|
| **QUICKLIST** | `OBJ_ENCODING_QUICKLIST` | 快速列表 | 默认 |
| **LISTPACK** | `OBJ_ENCODING_LISTPACK` | 紧凑列表 | Redis 7.0+ 优化 |

#### QUICKLIST 结构

**文件:** `src/quicklist.h`

```c
typedef struct quicklistNode {
    struct quicklistNode *prev;
    struct quicklistNode *next;
    unsigned char *entry;    // 指向 listpack
    size_t sz;               // listpack 大小
    unsigned int count : 16; // 元素个数
    unsigned int encoding : 2;  // RAW(1) 或 LZF(2)
    unsigned int container : 2; // PLAIN(1) 或 PACKED(2)
    unsigned int recompress : 1;
    unsigned int attempted_compress : 1;
    unsigned int dont_compress : 1;
    unsigned int extra : 9;
} quicklistNode;

typedef struct quicklist {
    quicklistNode *head;
    quicklistNode *tail;
    unsigned long count;     // 总元素数
    unsigned long len;       // quicklistNode 数量
    int fill : 16;           // 每个节点的最大元素数
    unsigned int compress : 16; // 压缩深度
} quicklist;
```

**内存布局:**
```
quicklist
└── head ──→ quicklistNode ──→ listpack
│            [prev|next|entry|sz|count|flags]
│                                   │
└── tail ──→ quicklistNode ──→ listpack
```

#### 特点
- 每个节点是 listpack，可配置每个节点的元素数量
- 支持 LZF 压缩
- 双向链表，支持从两端操作

#### LISTPACK 结构

**文件:** `src/listpack.h`

```c
typedef struct {
    unsigned char *sval;  // 字符串值
    uint32_t slen;        // 字符串长度
    long long lval;       // 整数值
} listpackEntry;
```

**内存布局:**
```
+-------+-------+-------+---+-------+
| total | count | ele1  |...| eleN  |
+-------+-------+-------+---+-------+
|  6B   |  2B   |       |   |       |
```

**编码类型:**
- `LP_ENCODING_INT`: 整数
- `LP_ENCODING_STRING`: 字符串

#### 特点
- 连续内存，提高缓存效率
- 相比 ziplist，简化实现，避免连锁更新

---

### 3. Set（集合）

#### 命令

`SADD`, `SREM`, `SMEMBERS`, `SINTER`

#### 实现文件

`src/t_set.c`

#### 编码方式

| 编码 | 宏定义 | 说明 | 使用场景 |
|------|--------|------|----------|
| **INTSET** | `OBJ_ENCODING_INTSET` | 整数集合 | 元素都是整数 |
| **HT** | `OBJ_ENCODING_HT` | 哈希表 | 有非整数元素 |
| **LISTPACK** | `OBJ_ENCODING_LISTPACK` | 紧凑列表 | Redis 7.0+ |

#### INTSET 结构

**文件:** `src/intset.h`

```c
typedef struct intset {
    uint32_t encoding;  // INTSET_ENC_INT16/32/64
    uint32_t length;    // 元素数量
    int8_t contents[];  // 有序数组
} intset;
```

#### 特点
- 有序数组存储整数
- 根据元素值大小选择 16/32/64 位编码
- 自动升级编码（16→32→64）

**示例:**
```redis
SADD numbers 1 2 3
// encoding=INTSET_ENC_INT16
// contents = [1, 2, 3]
```

#### HT (哈希表) 结构

当集合包含非整数元素时，使用 Redis 的 `dict` 哈希表：

```c
typedef struct dict {
    dictType *type;
    dictEntry **ht_table[2];  // 两个哈希表（用于rehash）
    unsigned long ht_used[2];
    long rehashidx;           // rehash 索引
    int16_t pauserehash;      // rehash 暂停标志
} dict;
```

#### 特点
- O(1) 平均查找时间
- 支持渐进式 rehash
- 自动扩容

---

### 4. Hash（哈希）

#### 命令

`HSET`, `HGET`, `HDEL`, `HKEYS`

#### 实现文件

`src/t_hash.c`

#### 编码方式

| 编码 | 宏定义 | 说明 | 使用场景 |
|------|--------|------|----------|
| **LISTPACK** | `OBJ_ENCODING_LISTPACK` | 紧凑列表 | 元素少且值小 |
| **LISTPACK_EX** | `OBJ_ENCODING_LISTPACK_EX` | 扩展列表包 | Redis 7.0+（带子键过期） |
| **HT** | `OBJ_ENCODING_HT` | 哈希表 | 元素多或值大 |

#### 编码转换条件

```c
// src/t_hash.c
// LISTPACK → HT 转换:
// 1. 元素数量 > hash_max_listpack_entries (默认512)
// 2. 任意 field 或 value 长度 > hash_max_listpack_value (默认64)
```

#### LISTPACK 存储方式

```c
// Listpack 中的存储格式:
// [field1, value1, field2, value2, ...]
```

**示例:**
```redis
HSET user:1 name "alice" age 30
// 在 listpack 中:
// ["name", "alice", "age", "30"]
```

---

### 5. Sorted Set（有序集合）

#### 命令

`ZADD`, `ZRANGE`, `ZREVRANGE`, `ZSCORE`

#### 实现文件

`src/t_zset.c`

#### 编码方式

| 编码 | 宏定义 | 说明 | 使用场景 |
|------|--------|------|----------|
| **LISTPACK** | `OBJ_ENCODING_LISTPACK` | 紧凑列表 | 元素少且小 |
| **SKIPLIST** | `OBJ_ENCODING_SKIPLIST` | 跳表 | 元素多或大 |

#### 编码转换条件

```c
// src/t_zset.c
// LISTPACK → SKIPLIST 转换:
// 1. 元素数量 > zset_max_listpack_entries (默认 128)
// 2. 任意元素值 > zset_max_listpack_value (默认 64 字节)
```

#### SKIPLIST 结构

```c
typedef struct zset {
    dict *dict;      // 哈希表：O(1) 查找成员
    zskiplist *zsl;  // 跳表：O(log N) 范围查询
} zset;

typedef struct zskiplistNode {
    sds ele;                      // 成员
    double score;                 // 分数
    struct zskiplistNode *backward;
    struct zskiplistLevel {
        struct zskiplistNode *forward;
        unsigned long span;
    } level[];
} zskiplistNode;

typedef struct zskiplist {
    struct zskiplistNode *header, *tail;
    unsigned long length;  // 元素数量
    int level;             // 最大层数
} zskiplist;
```

**内存布局:**
```
zset
├── dict ──→ {member → score}  // O(1) 查分数
└── zsl ──→ zskiplist ──→ ... [header]
                   │
                   └─→ node [level0|level1|level2] ──→ score:4.0
                                                   │   ele:"redis"
                                                   └─→ score:5.0
                                                       ele:"memcached"
```

**跳表优势:**
- O(log N) 查找、插入、删除
- 支持范围查询
- 通过 dict + zskiplist 组合实现霍尔兹张果与范围查询的高效平衡

---

### 6. Stream（流）

#### 命令

`XADD`, `XREAD`, `XGROUP`, `XREADGROUP`

#### 实现文件

`src/t_stream.c`

#### 编码方式

| 编码 | 宏定义 | 说明 |
|------|--------|------|
| **STREAM** | `OBJ_ENCODING_STREAM` | Radix 树 + Listpack |

#### 数据结构

```c
typedef struct stream {
    rax *rax;              // Radix 树：key=StreamID, value=listpack
    uint64_t length;       // 消息数量
    streamID last_id;      // 最后 ID
    rax *cgroups;          // Consumer Groups
} stream;

typedef struct streamID {
    uint64_t ms;      // 毫秒时间戳
    uint64_t seq;     // 序列号
} streamID;
```

**内存布局:**
```
stream
└── rax ──→ radix tree
           root
          /    \
     [00]       [11]
      │           │
  listpack1   listpack2
  [entry1]    [entry3]
  [entry2]    [entry4]
```

**Radix 树 (RAX):**
- 空间紧凑的前缀树
- 适合存储有序的 ID 序列
- O(k) 查找（k 为 key 长度）

#### 特点
- 高性能的消息流处理
- 支持消费者组
- 支持范围读取

---

### 7. Module（模块类型）

#### 说明

由 Redis 模块实现的自定义类型

#### 示例模块
- RedisJSON (JSON 类型)
- RedisTimeSeries (时间序列)
- RedisBloom (布隆过滤器)
- RediSearch (全文搜索)

---

## 二、基础类型（底层数据结构）

Redis 实现了多种底层数据结构来优化不同类型的数据存储：

### 1. SDS (Simple Dynamic String)

#### 文件

`src/sds.h`, `src/sds.c`

#### SDS 类型

5 种 SDS 类型：

```c
sdshdr5  // 0-31 字节    (3 bits len in flags)
sdshdr8  // 32-255 字节  (1B len, 1B alloc)
sdshdr16 // 256-65535    (2B len, 2B alloc)
sdshdr32 // 65536-4GB    (4B len, 4B alloc)
sdshdr64 // >4GB         (8B len, 8B alloc)
```

**结构:**
```c
struct sdshdr8 {
    uint8_t len;        // 已用长度
    uint8_t alloc;      // 已分配长度
    unsigned char flags;// 类型标志
    char buf[];         // 数据
};
```

#### 优势
- O(1) 获取长度
- 二进制安全
- 预分配 + 惰性释放
- 兼容 C 字符串

---

### 2. Listpack

#### 文件

`src/listpack.h`, `src/listpack.c`

#### 内存布局
```
+-------+-------+-------+-------+-------+-------+-------+
| total | count |  ele1 |  ele2 |  ...  |  eleN | 0xFF  |
+-------+-------+-------+-------+-------+-------+-------+
|  4B   |  2B   |       |       |       |       |  1B   |
```

**编码:**
```c
LP_ENCODING_INT     // 整数
LP_ENCODING_7BIT_UINT   // 7位无符号整数
LP_ENCODING_13BIT_INT   // 13位整数
LP_ENCODING_16BIT_INT   // 16位整数
LP_ENCODING_STRING  // 字符串
LP_ENCODING_6BIT_STR    // 6位长度字符串
LP_ENCODING_12BIT_STR   // 12位长度字符串
```

#### 特点
- 连续内存，提高缓存效率
- 简化实现，避免连锁更新
- 替代 ziplist

---

### 3. Dict (哈希表)

#### 文件

`src/dict.h`, `src/dict.c`

```c
typedef struct dictEntry {
    void *key;
    union {
        void *val;
        uint64_t u64;
        int64_t s64;
        double d;
    } v;
    struct dictEntry *next;
} dictEntry;

typedef struct dict {
    dictType *type;
    dictEntry **ht_table[2];  // 两个表（rehash）
    unsigned long ht_used[2];
    long rehashidx;
    int16_t pauserehash;
} dict;
```

#### Rehash 策略
- 渐进式 rehash
- 每次操作只迁移少量元素
- 分摊执行成本

---

### 4. Intset (整数集合)

#### 文件

`src/intset.h`, `src/intset.c`

```c
typedef struct intset {
    uint32_t encoding;  // INTSET_ENC_INT16/32/64
    uint32_t length;    // 元素数量
    int8_t contents[];  // 有序数组
} intset;
```

#### 编码升级
```
1. 初始: INTSET_ENC_INT16
2. 添加 >32767: 升级到 INTSET_ENC_INT32
3. 添加 >2^31-1: 升级到 INTSET_ENC_INT64
```

---

### 5. Quicklist (快速列表)

#### 文件

`src/quicklist.h`, `src/quicklist.c`

```c
typedef struct quicklistNode {
    struct quicklistNode *prev;
    struct quicklistNode *next;
    unsigned char *entry;    // listpack
    size_t sz;
    unsigned int count : 16;
} quicklistNode;

typedef struct quicklist {
    quicklistNode *head;
    quicklistNode *tail;
    unsigned long count;
    unsigned long len;
    int fill : 16;
    unsigned int compress : 16;
} quicklist;
```

#### 优化
- 每个节点是 listpack
- 支持 LZF 压缩
- 双向链表

---

### 6. Skip List (跳表)

#### 文件

`src/server.h`

```c
typedef struct zskiplistNode {
    sds ele;
    double score;
    struct zskiplistNode *backward;
    struct zskiplistLevel {
        struct zskiplistNode *forward;
        unsigned long span;
    } level[];
} zskiplistNode;
```

#### 特点
- O(log N) 查找
- 支持范围查询
- 实现简单

---

### 7. Rax (基数树)

#### 文件

`src/rax.h`, `src/rax.c`

```c
typedef struct raxNode {
    uint32_t iskey:1;     // 是否为 key
    uint32_t isnull:1;    // value 是否为 NULL
    uint32_t iscompr:1;   // 是否压缩
    uint32_t size:29;     // 子节点数量
    unsigned char data[]; // 键值 + 子节点指针
} raxNode;
```

**压缩节点:**
```
+---+---+---+---+---+
| flags | len | string | children |
+---+---+---+---+---+
```

#### 特点
- 空间效率高
- 适合有序 key

---

## 类型与编码映射

### 完整映射表

| 对象类型 | 编码类型 | 编码宏 | 底层结构 |
|---------|---------|-------|----------|
| **STRING** | INT | `OBJ_ENCODING_INT` | 整数 |
| | EMBSTR | `OBJ_ENCODING_EMBSTR` | SDS (小字符串) |
| | RAW | `OBJ_ENCODING_RAW` | SDS |
| **LIST** | QUICKLIST | `OBJ_ENCODING_QUICKLIST` | Quicklist (listpack) |
| | LISTPACK | `OBJ_ENCODING_LISTPACK` | Listpack |
| **SET** | INTSET | `OBJ_ENCODING_INTSET` | Intset |
| | HT | `OBJ_ENCODING_HT` | Dict |
| | LISTPACK | `OBJ_ENCODING_LISTPACK` | Listpack |
| **ZSET** | LISTPACK | `OBJ_ENCODING_LISTPACK` | Listpack |
| | SKIPLIST | `OBJ_ENCODING_SKIPLIST` | Zset (dict+zskiplist) |
| **HASH** | LISTPACK | `OBJ_ENCODING_LISTPACK` | Listpack |
| | LISTPACK_EX | `OBJ_ENCODING_LISTPACK_EX` | Listpack + 过期 |
| | HT | `OBJ_ENCODING_HT` | Dict |
| **STREAM** | STREAM | `OBJ_ENCODING_STREAM` | Rax + Listpack |

### 编码选择策略

**Redis 遵循以下原则:**
1. 小数据优先使用紧凑编码（LISTPACK, INTSET）
2. 大数据使用高效索引结构（SKIPLIST, HT）
3. 自动升级转换（LISTPACK → HT）
4. 类型与编码分离设计

---

## 内存优化

### 1. 小对象优化

**EMBSTR 编码:**
```c
// 44 字节以内的小字符串
SET key "hello"
// 节省一次内存分配，提高缓存命中率
```

**共享整数对象:**
```c
// 0-9999 的整数共享
for (i = 0; i < 10000; i++) {
    shared.integers[i] = createObject(...);  // 全局共享
}
```

### 2. 紧凑编码

**Listpack vs Ziplist:**
- Listpack 避免连锁更新
- 更高效的编码
- 更低的内存开销

### 3. 压缩

**Quicklist LZF 压缩:**
- 可配置压缩深度
- 惰性压缩
- 降低内存占用

---

## 调试技巧

### 查看对象编码

```
# 查看对象类型
TYPE mykey

# 查看对象编码
OBJECT ENCODING mykey
# 返回: int, embstr, raw, quicklist, listpack, intset, hashtable, skiplist

# 查看对象详细信息
DEBUG OBJECT mykey
```

### 内存分析

```
# 查看内存使用
MEMORY USAGE mykey

# 查看内存统计
INFO memory

# 查看键空间统计
INFO keyspace
```

---

## 源码关键文件

| 数据类型 | 实现文件 | 头文件 |
|---------|---------|--------|
| String | `src/t_string.c` | - |
| List | `src/t_list.c` | - |
| Set | `src/t_set.c` | - |
| Hash | `src/t_hash.c` | - |
| ZSet | `src/t_zset.c` | - |
| Stream | `src/t_stream.c` | - |
| SDS | `src/sds.c` | `src/sds.h` |
| Listpack | `src/listpack.c` | `src/listpack.h` |
| Dict | `src/dict.c` | `src/dict.h` |
| Intset | `src/intset.c` | `src/intset.h` |
| Quicklist | `src/quicklist.c` | `src/quicklist.h` |
| Rax | `src/rax.c` | `src/rax.h` |
| Object | `src/object.c` | `src/server.h` |

---

## 总结

Redis 的数据类型系统具有以下特点：

1. **统一对象模型**: 所有类型通过 `redisObject` 统一管理
2. **多种编码**: 每种类型支持多种编码，自动选择最优方案
3. **内存优化**: 小对象优化、紧凑编码、共享对象等策略
4. **性能平衡**: 在不同场景下自动选择编码，平衡内存和性能
5. **渐进式演进**: 从 ziplist 到 listpack，不断优化

参考资料：
- [Redis 命令执行流程](redis_cli_cmd.md)
- [Redis 调试指南](redis-debug.md)