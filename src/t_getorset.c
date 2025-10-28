/*
 * Copyright (c) 2009-Present, Redis Ltd.
 * All rights reserved.
 *
 * Licensed under your choice of (a) the Redis Source Available License 2.0
 * (RSALv2); or (b) the Server Side Public License v1 (SSPLv1); or (c) the
 * GNU Affero General Public License v3 (AGPLv3).
 */

#include "server.h"

/* GET_OR_SET key default_value
 * - If key exists: return current value
 * - If key does not exist: set default_value and return it
 */
void getOrSetCommand(client *c) {
    robj *key = c->argv[1];
    robj *value = c->argv[2];
    
    // Lookup the key
    robj *o = lookupKeyRead(c->db, key);
    
    if (o == NULL) {
        // Key does not exist: set new value
        // Try to encode the value for optimization
        value = tryObjectEncoding(value);
        
        // Set the key with default value
        setKey(c, c->db, key, &value, 0);
        
        // Increment reference count
        incrRefCount(value);
        
        // Mark database as modified
        server.dirty++;
        
        // Send keyspace notification
        notifyKeyspaceEvent(NOTIFY_STRING, "set", key, c->db->id);
        
        // Return the newly set value
        addReplyBulk(c, value);
        
        serverLog(LL_DEBUG, "GET_OR_SET: created key %s", 
                  (char*)key->ptr);
    } else {
        // Key exists: return current value
        if (checkType(c, o, OBJ_STRING)) {
            return;
        }
        addReplyBulk(c, o);
        
        serverLog(LL_DEBUG, "GET_OR_SET: returned existing value for %s", 
                  (char*)key->ptr);
    }
}

/* Get keys function for Redis Cluster */
int getOrSetGetKeys(struct redisCommand *cmd, robj **argv, int argc, 
                    getKeysResult *result) {
    UNUSED(cmd);
    
    if (argc >= 3) {
        keyReference *keys;
        keys = getKeysPrepareResult(result, 1);
        keys[0].pos = 1;  // key at position 1 (argv[1])
        keys[0].flags = CMD_KEY_RW;
        result->numkeys = 1;
    }
    return C_OK;
}
