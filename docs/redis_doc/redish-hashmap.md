## Redis Hashmap (哈希表) 设计与实现

### 概述
Redis 的 Hashmap 是一种键值对存储数据结构，用于实现哈希数据类型。它采用**渐进式编码**策略，根据数据规模自动选择最适合的底层实现方式。

### 设计目标
1. **内存效率**: 小哈希使用紧凑的 listpack 存储，减少内存开销
2. **性能平衡**: 大数据量时切换到 hashtable，提供 O(1) 查找性能
3. **字段过期**: 支持为每个哈希字段设置独立的 TTL（Hash Field Expiration）
4. **渐进转换**: 根据阈值自动从 listpack 升级到 hashtable

### 使用场景
- 存储对象属性（如用户信息、商品属性）
- 缓存关联数据
- 需要独立设置字段 TTL 的场景
- 替代多个 key-value 对，减少键空间占用

### 文档结构
* 数据结构定义 - Listpack、ListpackEx、Hashtable 编码
* 编码转换机制 - 阈值和转换条件
* Listpack 编码操作 - 字段查找、插入、更新
* Hashtable 编码操作 - 哈希表操作和字段管理
* 字段过期（HFE） - TTL 设置和过期处理
* 关键参数配置 - 编码切换阈值
* 性能分析 - 时间和空间复杂度对比

---

## 数据结构定义

### Hash 对象编码类型
Redis Hash 支持**三种编码**：

```c
// object.c:477-482
robj *createHashObject(void) {
    unsigned char *zl = lpNew(0);
    robj *o = createObject(OBJ_HASH, zl);
    o->encoding = OBJ_ENCODING_LISTPACK;  // 默认 listpack 编码
    return o;
}
```

#### 1. OBJ_ENCODING_LISTPACK
**紧凑编码**，用于小哈希（默认）
- 内存连续存储
- 字段值成对出现：`field1, value1, field2, value2, ...`
- 无内存指针开销

#### 2. OBJ_ENCODING_LISTPACK_EX
**带过期元数据的 listpack**
- 字段值 TTL 三元组：`field1, value1, ttl1, field2, value2, ttl2, ...`
- 按 TTL 排序（最小 TTL 在前）
- TTL 未设置时存储 `HASH_LP_NO_TTL (0)`

```c
// t_hash.c:284-290
struct listpackEx {
    struct {
        unsigned int trash:1;           // 标记是否无效
        uint64_t meta_reserved:63;      // 保留位
    } meta;
    unsigned char *lp;                  // listpack 指针
};
```

#### 3. OBJ_ENCODING_HT
**哈希表编码**，用于大哈希
- 使用 Redis 的 `dict` 数据结构
- O(1) 平均时间复杂度
- 支持字段过期元数据

```c
// dictType 定义
dictType mstrHashDictType = {
    dictSdsHash,                        // 哈希函数
    NULL,                               // key dup
    NULL,                               // val dup
    dictSdsMstrKeyCompare,              // 键比较
    dictHfieldDestructor,                // 字段析构
    dictSdsDestructor,                   // 值析构
    .storedHashFunction = dictMstrHash,
    .storedKeyCompare = dictHfieldKeyCompare,
};
```

### 关键参数

```c
// server.h:2204-2205
size_t hash_max_listpack_entries;      // 默认: 512
size_t hash_max_listpack_value;        // 默认: 64

// config.c:3252, 3258
createSizeTConfig("hash-max-listpack-entries", ..., 512, ...)
createSizeTConfig("hash-max-listpack-value", ..., 64, ...)
```

**配置含义**：
- `hash-max-listpack-entries`: listpack 最大字段数（默认 512）
- `hash-max-listpack-value`: listpack 字段/值最大长度（默认 64 字节）

---

## 编码转换机制

### 转换触发条件

Hash 对象会从 listpack 自动转换为 hashtable，当满足以下任一条件：

#### 1. 字段数量超限
```c
// t_hash.c:924-925
if (hashTypeLength(o, 0) > server.hash_max_listpack_entries)
    hashTypeConvert(db, o, OBJ_ENCODING_HT);
```

#### 2. 字段/值长度超限
```c
// t_hash.c:890-891
if (sdslen(field) > server.hash_max_listpack_value || 
    sdslen(value) > server.hash_max_listpack_value)
    hashTypeConvert(db, o, OBJ_ENCODING_HT);
```

#### 3. 预检查优化
```c
// t_hash.c:606-609
size_t new_fields = (end - start + 1) / 2;
if (new_fields > server.hash_max_listpack_entries) {
    hashTypeConvert(db, o, OBJ_ENCODING_HT);
    dictExpand(o->ptr, new_fields);  // 预扩容
    return;
}
```

### 转换流程

#### Listpack → Hashtable
```c
// t_hash.c:1539-1595
void hashTypeConvertListpack(robj *o, int enc) {
    if (enc == OBJ_ENCODING_HT) {
        dict *dict = dictCreate(&mstrHashDictType);
        hashTypeIterator *hi = hashTypeInitIterator(o);
        
        // 遍历所有字段值对
        while (hashTypeNext(hi) != C_ERR) {
            sds field = hashTypeCurrentObjectNewSds(hi, OBJ_HASH_KEY);
            sds value = hashTypeCurrentObjectNewSds(hi, OBJ_HASH_VALUE);
            
            // 添加到 hashtable
            hfield newField = hfieldNew(field, sdslen(field), 0);
            dictAdd(dict, newField, value);
        }
        
        hashTypeReleaseIterator(hi);
        zfree(o->ptr);
        o->encoding = OBJ_ENCODING_HT;
        o->ptr = dict;
    }
}
```

---

## Listpack 编码操作

### 字段查找
```c
// t_hash.c:895-910
if (o->encoding == OBJ_ENCODING_LISTPACK) {
    unsigned char *zl = o->ptr;
    unsigned char *fptr = lpFirst(zl);
    
    if (fptr != NULL) {
        // 在 listpack 中查找字段（字段间隔为 1）
        fptr = lpFind(zl, fptr, (unsigned char*)field, sdslen(field), 1);
        if (fptr != NULL) {
            // 获取值指针
            unsigned char *vptr = lpNext(zl, fptr);
            // 返回值...
        }
    }
}
```

**时间复杂度**: O(N)，需要线性遍历

### 字段插入/更新
```c
// t_hash.c:912-920
if (!update) {
    listpackEntry entries[2] = {
        {.sval = (unsigned char*) field, .slen = sdslen(field)},
        {.sval = (unsigned char*) value, .slen = sdslen(value)},
    };
    
    // 追加到 listpack 尾部
    zl = lpBatchAppend(zl, entries, 2);
}
```

**操作流程**：
1. 查找字段是否存在
2. 存在则替换值
3. 不存在则追加到尾部
4. 检查是否需要转换为 hashtable

---

## Hashtable 编码操作

### 字段设置
```c
// t_hash.c:966-989
else if (o->encoding == OBJ_ENCODING_HT) {
    dict *ht = o->ptr;
    dictEntryLink bucket, link = dictFindLink(ht, field, &bucket);
    
    if (link == NULL) {
        // 字段不存在，创建新字段
        hfield newField = hfieldNew(field, sdslen(field), 0);
        dictSetKeyAtLink(ht, newField, &bucket, 1);
        de = *bucket;
    } else {
        // 字段存在，更新值
        de = *link;
        if (!(flags & HASH_SET_KEEP_TTL)) {
            // 处理 TTL...
        }
    }
    
    // 设置值
    dictSetVal(ht, de, value);
}
```

**时间复杂度**: O(1) 平均，O(N) 最坏（哈希冲突）

### mstr 字段对象
为了支持字段 TTL，Hash 使用 `mstr`（带元数据的不可变字符串）存储字段：

```c
// t_hash.c:973
hfield newField = hfieldNew(field, sdslen(field), 0);

// hfield 定义（基于 mstr）
typedef struct {
    mstr base;              // 基础字符串结构
    ExpireMeta *expireMeta; // TTL 元数据（可选）
} hfield;
```

---

## 字段过期（Hash Field Expiration）

### 功能特性
- 为每个哈希字段设置独立的 TTL
- 支持全局 HFE（Hash Field Expiration）主动过期
- 字段过期后自动从哈希中删除

### TTL 设置流程

```c
// t_hash.c:211-216
typedef struct HashTypeSetEx {
    ExpireSetCond expireSetCond;        // [XX | NX | GT | LT]
    uint64_t minExpire;                 // 最小过期时间
    redisDb *db;
    robj *key, *hashObj;
    uint64_t minExpireFields;
    client *c;
    const char *cmd;
} HashTypeSetEx;
```

**操作序列**：
1. `hashTypeSetExInit()` - 初始化 HFE 上下文
2. `hashTypeSetEx()` - 设置字段 TTL
3. `hashTypeSetExDone()` - 完成并更新全局 HFE

### ListpackEx 的过期元数据

```c
// t_hash.c:284
#define HASH_LP_NO_TTL 0

// listpackEx 结构
struct listpackEx {
    struct {
        unsigned int trash:1;
        uint64_t meta_reserved:63;
    } meta;
    unsigned char *lp;  // 格式: field1, value1, ttl1, field2, value2, ttl2...
};
```

**特点**：
- TTL 未设置时存储 `HASH_LP_NO_TTL (0)`
- 字段按 TTL 排序（最小 TTL 在前）
- 便于快速查找即将过期的字段

---

## 关键操作详解

### HSET 命令实现
```c
// t_hash.c:882-1014
int hashTypeSet(redisDb *db, kvobj *o, sds field, sds value, int flags) {
    int update = 0;
    
    // 1. 检查是否需要转换编码
    if (o->encoding == OBJ_ENCODING_LISTPACK ||
        o->encoding == OBJ_ENCODING_LISTPACK_EX) {
        if (sdslen(field) > server.hash_max_listpack_value || 
            sdslen(value) > server.hash_max_listpack_value)
            hashTypeConvert(db, o, OBJ_ENCODING_HT);
    }
    
    // 2. 根据编码执行设置操作
    if (o->encoding == OBJ_ENCODING_LISTPACK) {
        // Listpack 操作...
    } else if (o->encoding == OBJ_ENCODING_LISTPACK_EX) {
        // ListpackEx 操作（处理 TTL）...
    } else if (o->encoding == OBJ_ENCODING_HT) {
        // Hashtable 操作...
    }
    
    // 3. 检查是否需要转换为 hashtable
    if (hashTypeLength(o, 0) > server.hash_max_listpack_entries)
        hashTypeConvert(db, o, OBJ_ENCODING_HT);
    
    return update;
}
```

### HMSET 批量设置优化
```c
// t_hash.c:580-625
void hashTypeTryConversion(redisDb *db, robj *o, robj **argv, int start, int end) {
    // 预检查：如果新字段数超过阈值，提前转换
    size_t new_fields = (end - start + 1) / 2;
    if (new_fields > server.hash_max_listpack_entries) {
        hashTypeConvert(db, o, OBJ_ENCODING_HT);
        dictExpand(o->ptr, new_fields);  // 预扩容
        return;
    }
    
    // 检查字段/值长度
    for (i = start; i <= end; i++) {
        if (len > server.hash_max_listpack_value) {
            hashTypeConvert(db, o, OBJ_ENCODING_HT);
            return;
        }
    }
}
```

---

## 性能分析

### 时间复杂度对比

| 操作 | Listpack | Hashtable |
|------|----------|-----------|
| HGET | O(N) | O(1) 平均 |
| HSET | O(N) | O(1) 平均 |
| HDEL | O(N) | O(1) 平均 |
| HLEN | O(1) | O(1) |
| HGETALL | O(N) | O(N) |

### 空间复杂度

#### Listpack 编码
- **优点**: 紧凑存储，无指针开销
- **缺点**: 线性查找慢
- **适用**: 小哈希（< 512 字段，值 < 64 字节）

#### Hashtable 编码
- **优点**: O(1) 查找，性能好
- **缺点**: 内存开销大（指针 + 元数据）
- **适用**: 大哈希或字段/值长度超过阈值

### 编码切换开销

**转换成本**：
- 需要遍历所有 listpack 元素
- 创建新的 hashtable
- 迁移所有字段值对
- 额外内存分配

**优化策略**：
- HMSET 批量操作时预检查并提前转换
- 使用 `dictExpand()` 预扩容，减少哈希表 rehash

---

## 实际应用示例

### 示例 1: 用户信息存储
```redis
HMSET user:1001 name "Alice" age "25" email "alice@example.com"
```

**内存布局**（Listpack 编码）：
```
内存地址:  [0x1000] [0x1001] [0x1002] ...
内容:      | count  | 'name' | 'Alice' | 'age' | '25' | 'email' | 'alice@...' |
```

### 示例 2: 大哈希自动转换
```redis
# 假设 hash-max-listpack-entries = 512
HMSET big_hash f1 v1 f2 v2 ... f513 v513  # 触发转换为 hashtable
```

**转换后**：
- 编码：`OBJ_ENCODING_LISTPACK` → `OBJ_ENCODING_HT`
- 底层：listpack → dict (hashtable)
- 查找：O(N) → O(1)

### 示例 3: 字段过期
```redis
HSET myhash field1 value1
HEXPIRE myhash field1 300  # 设置 field1 的 TTL 为 300 秒
```

**编码变化**：
- `OBJ_ENCODING_LISTPACK` → `OBJ_ENCODING_LISTPACK_EX`
- 添加过期元数据到 listpack

---

## 配置调优建议

### 内存优先场景
```redis
CONFIG SET hash-max-listpack-entries 128
CONFIG SET hash-max-listpack-value 32
```
- 更多哈希使用 listpack
- 内存占用更小
- 查询性能略慢

### 性能优先场景
```redis
CONFIG SET hash-max-listpack-entries 256
CONFIG SET hash-max-listpack-value 128
```
- 较少哈希使用 listpack
- 更早切换到 hashtable
- 查询性能更好

### 监控指标
- `OBJECT ENCODING key` - 查看哈希的编码类型
- `MEMORY USAGE key` - 查看内存占用
- Redis INFO - 监控哈希大小分布

---

## 总结

Redis Hashmap 的设计亮点：

1. **渐进式编码**: 根据数据规模自动选择最优编码
2. **内存优化**: listpack 减少小哈希的内存开销
3. **性能平衡**: hashtable 提供高效的查找性能
4. **字段过期**: 支持细粒度的 TTL 控制
5. **平滑转换**: 自动处理编码升级，对用户透明

**适用场景**：
- ✅ 存储对象属性（用户信息、商品属性）
- ✅ 缓存关联数据
- ✅ 需要独立字段过期的场景
- ❌ 需要频繁按模式查找（考虑 Sorted Set）
- ❌ 需要范围查询（考虑 Sorted Set）

