/*
 * modgetorset - Redis Module for MOD_GET_OR_SET command
 *
 * Copyright (c) 2025
 * Licensed under your choice of the Redis Source Available License 2.0
 * or the Server Side Public License v1.
 */

#include "redismodule.h"

#ifndef UNUSED
#define UNUSED(x) ((void)(x))
#endif

/* MOD_GET_OR_SET key default_value
 *
 * 如果 key 存在，则返回当前值；
 * 如果 key 不存在，则将 default_value 赋值并返回该值。
 */
int ModGetOrSet_RedisCommand(RedisModuleCtx *ctx, RedisModuleString **argv, int argc) {
    // 参数校验
    if (argc != 3) {
        return RedisModule_WrongArity(ctx);
    }

    RedisModuleString *key = argv[1];
    RedisModuleString *default_value = argv[2];

    // 打开 key（读写模式）
    RedisModuleKey *keyobj = RedisModule_OpenKey(ctx, key, REDISMODULE_READ | REDISMODULE_WRITE);
    if (keyobj == NULL) {
        RedisModule_ReplyWithError(ctx, "ERR could not open key");
        return REDISMODULE_OK;
    }

    int type = RedisModule_KeyType(keyobj);

    if (type == REDISMODULE_KEYTYPE_EMPTY) {
        // 不存在，设置并返回 default_value
        if (RedisModule_StringSet(keyobj, default_value) != REDISMODULE_OK) {
            RedisModule_CloseKey(keyobj);
            RedisModule_ReplyWithError(ctx, "ERR failed to set value");
            return REDISMODULE_OK;
        }
        RedisModule_ReplyWithString(ctx, default_value);
    } else if (type == REDISMODULE_KEYTYPE_STRING) {
        // 存在，获取当前值
        size_t len;
        const char *val = RedisModule_StringDMA(keyobj, &len, REDISMODULE_READ);
        if (val) {
            RedisModule_ReplyWithStringBuffer(ctx, val, len);
        } else {
            // 如果 DMA 失败，使用另一种方式获取值
            // 通过 key->kv 获取 robj，然后转换为 RedisModuleString
            RedisModule_ReplyWithError(ctx, "ERR failed to get string value");
        }
    } else {
        RedisModule_CloseKey(keyobj);
        return RedisModule_ReplyWithError(ctx, "WRONGTYPE Operation against a key holding the wrong kind of value");
    }

    RedisModule_CloseKey(keyobj);
    return REDISMODULE_OK;
}

int RedisModule_OnLoad(RedisModuleCtx *ctx, RedisModuleString **argv, int argc) {
    UNUSED(argv);
    UNUSED(argc);
    
    if (RedisModule_Init(ctx, "modgetorset", 1, REDISMODULE_APIVER_1) == REDISMODULE_ERR) {
        return REDISMODULE_ERR;
    }
    if (RedisModule_CreateCommand(
            ctx,
            "MOD_GET_OR_SET",
            ModGetOrSet_RedisCommand,
            "write deny-oom",
            1, 1, 1) == REDISMODULE_ERR) {
        return REDISMODULE_ERR;
    }
    return REDISMODULE_OK;
}
