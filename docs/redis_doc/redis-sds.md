# Redis String: 源码分析
* 理解概念
* 理解使用
* 深入源码分析


## sds 柔性数组

### 内存布局图解
* header + buf
* sds 是buf的地址
* s[initlen] = '\0'; 字符串安全

```
内存地址:  [0x1000] [0x1001] [0x1002] [0x1003] [0x1004] [0x1005] [0x1006] [0x1007] [0x1008] [0x1009] [0x100A] [0x100B] [0x100C] [0x100D] [0x100E] [0x100F]
           |-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|
内容:      |  len  | alloc | flags |  'H'  |  'e'  |  'l'  |  'l'  |  'o'  |  '\0' |       |       |       |       |       |       |
           |-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|
含义:      头部信息                    柔性数组buf[]存储实际字符串数据
```

```c
sds sdsnewplacement(char *buf, size_t bufsize, char type, const char *init, size_t initlen) {
    assert(bufsize >= sdsReqSize(initlen, type));
    int hdrlen = sdsHdrSize(type);
    size_t usable = bufsize - hdrlen - 1;
    // buf malloc 分配的内存地址
    sds s = buf + hdrlen;
    unsigned char *fp = ((unsigned char *)s) - 1; /* flags pointer. */

    switch(type) {
        case SDS_TYPE_5: {
            *fp = type | (initlen << SDS_TYPE_BITS);
            break;
        }
        case SDS_TYPE_8: {
            SDS_HDR_VAR(8,s);
            sh->len = initlen;
            debugAssert(usable <= sdsTypeMaxSize(type));
            sh->alloc = usable;
            *fp = type;
            break;
        }
        case SDS_TYPE_16: {
            SDS_HDR_VAR(16,s);
            sh->len = initlen;
            debugAssert(usable <= sdsTypeMaxSize(type));
            sh->alloc = usable;
            *fp = type;
            break;
        }
        case SDS_TYPE_32: {
            SDS_HDR_VAR(32,s);
            sh->len = initlen;
            debugAssert(usable <= sdsTypeMaxSize(type));
            sh->alloc = usable;
            *fp = type;
            break;
        }
        case SDS_TYPE_64: {
            SDS_HDR_VAR(64,s);
            sh->len = initlen;
            debugAssert(usable <= sdsTypeMaxSize(type));
            sh->alloc = usable;
            *fp = type;
            break;
        }
    }
    if (init == SDS_NOINIT)
        init = NULL;
    else if (!init)
        memset(s, 0, initlen);
    else if (initlen) 
        memcpy(s, init, initlen);

    s[initlen] = '\0';
    return s;
}
```