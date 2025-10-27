## 编译日志

```shell
venv) ➜  redis git:(feature/1.0) ✗ rm -rf src/.make-settings
(venv) ➜  redis git:(feature/1.0) ✗ compiledb make OPTIMIZATION=-O0 
## Building [make OPTIMIZATION=-O0]...
for dir in src; do /Applications/Xcode.app/Contents/Developer/usr/bin/make -C $dir all; done
    CC Makefile.dep
rm -rf redis-server redis-sentinel redis-cli redis-benchmark redis-check-rdb redis-check-aof *.o *.gcda *.gcno *.gcov redis.info lcov-html Makefile.dep *.so
rm -f threads_mngr.d memory_prefetch.d adlist.d quicklist.d ae.d anet.d dict.d ebuckets.d eventnotifier.d iothread.d mstr.d kvstore.d fwtree.d estore.d server.d sds.d zmalloc.d lzf_c.d lzf_d.d pqsort.d zipmap.d sha1.d ziplist.d release.d networking.d util.d object.d db.d replication.d rdb.d t_string.d t_list.d t_set.d t_zset.d t_hash.d config.d aof.d pubsub.d multi.d debug.d sort.d intset.d syncio.d cluster.d cluster_asm.d cluster_legacy.d cluster_slot_stats.d crc16.d endianconv.d slowlog.d eval.d bio.d rio.d rand.d memtest.d syscheck.d crcspeed.d crccombine.d crc64.d bitops.d sentinel.d notify.d setproctitle.d blocked.d hyperloglog.d latency.d sparkline.d redis-check-rdb.d redis-check-aof.d geo.d lazyfree.d module.d evict.d expire.d geohash.d geohash_helper.d childinfo.d defrag.d siphash.d rax.d t_stream.d listpack.d localtime.d lolwut.d lolwut5.d lolwut6.d lolwut8.d acl.d tracking.d socket.d tls.d sha256.d timeout.d setcpuaffinity.d monotonic.d mt19937-64.d resp_parser.d call_reply.d script_lua.d script.d functions.d function_lua.d commands.d strl.d connection.d unix.d logreqres.d hnsw.d vset.d vset_config.d anet.d adlist.d dict.d redis-cli.d zmalloc.d release.d ae.d redisassert.d crcspeed.d crccombine.d crc64.d siphash.d crc16.d monotonic.d cli_common.d mt19937-64.d strl.d cli_commands.d ae.d anet.d redis-benchmark.d adlist.d dict.d zmalloc.d redisassert.d release.d crcspeed.d crccombine.d crc64.d siphash.d crc16.d monotonic.d cli_common.d mt19937-64.d strl.d
(cd ../tests/modules && /Applications/Xcode.app/Contents/Developer/usr/bin/make clean)
rm -f commandfilter.so basics.so testrdb.so fork.so infotest.so propagate.so misc.so hooks.so blockonkeys.so blockonbackground.so scan.so datatype.so datatype2.so auth.so keyspace_events.so blockedclient.so getkeys.so getchannels.so test_lazyfree.so timer.so defragtest.so keyspecs.so hash.so zset.so stream.so mallocsize.so aclcheck.so list.so subcommands.so reply.so cmdintrospection.so eventloop.so moduleconfigs.so moduleconfigstwo.so publish.so usercall.so postnotifications.so moduleauthtwo.so rdbloadsave.so crash.so internalsecret.so configaccess.so atomicslotmigration.so commandfilter.xo basics.xo testrdb.xo fork.xo infotest.xo propagate.xo misc.xo hooks.xo blockonkeys.xo blockonbackground.xo scan.xo datatype.xo datatype2.xo auth.xo keyspace_events.xo blockedclient.xo getkeys.xo getchannels.xo test_lazyfree.xo timer.xo defragtest.xo keyspecs.xo hash.xo zset.xo stream.xo mallocsize.xo aclcheck.xo list.xo subcommands.xo reply.xo cmdintrospection.xo eventloop.xo moduleconfigs.xo moduleconfigstwo.xo publish.xo usercall.xo postnotifications.xo moduleauthtwo.xo rdbloadsave.xo crash.xo internalsecret.xo configaccess.xo atomicslotmigration.xo
(cd ../deps && /Applications/Xcode.app/Contents/Developer/usr/bin/make distclean)
(cd hiredis && /Applications/Xcode.app/Contents/Developer/usr/bin/make clean) > /dev/null || true
(cd linenoise && /Applications/Xcode.app/Contents/Developer/usr/bin/make clean) > /dev/null || true
(cd lua && /Applications/Xcode.app/Contents/Developer/usr/bin/make clean) > /dev/null || true
(cd jemalloc && [ -f Makefile ] && /Applications/Xcode.app/Contents/Developer/usr/bin/make distclean) > /dev/null || true
(cd hdr_histogram && /Applications/Xcode.app/Contents/Developer/usr/bin/make clean) > /dev/null || true
(cd fpconv && /Applications/Xcode.app/Contents/Developer/usr/bin/make clean) > /dev/null || true
(cd fast_float && /Applications/Xcode.app/Contents/Developer/usr/bin/make clean) > /dev/null || true
(cd xxhash && /Applications/Xcode.app/Contents/Developer/usr/bin/make clean) > /dev/null || true
make: *** tests: No such file or directory.  Stop.
make[3]: *** [clean] Error 2
(rm -f .make-*)
(cd modules && /Applications/Xcode.app/Contents/Developer/usr/bin/make clean)
rm -rf *.xo *.so
(cd ../tests/modules && /Applications/Xcode.app/Contents/Developer/usr/bin/make clean)
rm -f commandfilter.so basics.so testrdb.so fork.so infotest.so propagate.so misc.so hooks.so blockonkeys.so blockonbackground.so scan.so datatype.so datatype2.so auth.so keyspace_events.so blockedclient.so getkeys.so getchannels.so test_lazyfree.so timer.so defragtest.so keyspecs.so hash.so zset.so stream.so mallocsize.so aclcheck.so list.so subcommands.so reply.so cmdintrospection.so eventloop.so moduleconfigs.so moduleconfigstwo.so publish.so usercall.so postnotifications.so moduleauthtwo.so rdbloadsave.so crash.so internalsecret.so configaccess.so atomicslotmigration.so commandfilter.xo basics.xo testrdb.xo fork.xo infotest.xo propagate.xo misc.xo hooks.xo blockonkeys.xo blockonbackground.xo scan.xo datatype.xo datatype2.xo auth.xo keyspace_events.xo blockedclient.xo getkeys.xo getchannels.xo test_lazyfree.xo timer.xo defragtest.xo keyspecs.xo hash.xo zset.xo stream.xo mallocsize.xo aclcheck.xo list.xo subcommands.xo reply.xo cmdintrospection.xo eventloop.xo moduleconfigs.xo moduleconfigstwo.xo publish.xo usercall.xo postnotifications.xo moduleauthtwo.xo rdbloadsave.xo crash.xo internalsecret.xo configaccess.xo atomicslotmigration.xo
(rm -f .make-*)
echo STD=-pedantic -DREDIS_STATIC='' -Wno-c11-extensions -std=gnu11 >> .make-settings
echo WARN=-Wall -W -Wno-missing-field-initializers -Werror=deprecated-declarations -Wstrict-prototypes >> .make-settings
echo OPT=-O0 >> .make-settings
echo MALLOC=libc >> .make-settings
echo BUILD_TLS= >> .make-settings
echo USE_SYSTEMD= >> .make-settings
echo CFLAGS= >> .make-settings
echo LDFLAGS= >> .make-settings
echo REDIS_CFLAGS= >> .make-settings
echo REDIS_LDFLAGS= >> .make-settings
echo PREV_FINAL_CFLAGS=-pedantic -DREDIS_STATIC='' -Wno-c11-extensions -std=gnu11 -Wall -W -Wno-missing-field-initializers -Werror=deprecated-declarations -Wstrict-prototypes -O0 -g -ggdb   -I../deps/hiredis -I../deps/linenoise -I../deps/lua/src -I../deps/hdr_histogram -I../deps/fpconv -I../deps/fast_float -I../deps/xxhash -DINCLUDE_VEC_SETS=1 >> .make-settings
echo PREV_FINAL_LDFLAGS= -O0  -g -ggdb >> .make-settings
(cd ../deps && /Applications/Xcode.app/Contents/Developer/usr/bin/make hiredis linenoise lua hdr_histogram fpconv fast_float xxhash)
(cd hiredis && /Applications/Xcode.app/Contents/Developer/usr/bin/make clean) > /dev/null || true
(cd linenoise && /Applications/Xcode.app/Contents/Developer/usr/bin/make clean) > /dev/null || true
(cd lua && /Applications/Xcode.app/Contents/Developer/usr/bin/make clean) > /dev/null || true
(cd jemalloc && [ -f Makefile ] && /Applications/Xcode.app/Contents/Developer/usr/bin/make distclean) > /dev/null || true
(cd hdr_histogram && /Applications/Xcode.app/Contents/Developer/usr/bin/make clean) > /dev/null || true
(cd fpconv && /Applications/Xcode.app/Contents/Developer/usr/bin/make clean) > /dev/null || true
(cd fast_float && /Applications/Xcode.app/Contents/Developer/usr/bin/make clean) > /dev/null || true
(cd xxhash && /Applications/Xcode.app/Contents/Developer/usr/bin/make clean) > /dev/null || true
make: *** tests: No such file or directory.  Stop.
make[3]: *** [clean] Error 2
(rm -f .make-*)
(echo "" > .make-ldflags)
(echo "" > .make-cflags)
MAKE hiredis
cd hiredis && /Applications/Xcode.app/Contents/Developer/usr/bin/make static  HIREDIS_CFLAGS="" HIREDIS_LDFLAGS=""
cc -std=c99 -c -O0 -fPIC   -Wall -Wextra -Werror -Wstrict-prototypes -Wwrite-strings -Wno-missing-field-initializers -g -ggdb   -pedantic alloc.c
cc -std=c99 -c -O0 -fPIC   -Wall -Wextra -Werror -Wstrict-prototypes -Wwrite-strings -Wno-missing-field-initializers -g -ggdb   -pedantic net.c
cc -std=c99 -c -O0 -fPIC   -Wall -Wextra -Werror -Wstrict-prototypes -Wwrite-strings -Wno-missing-field-initializers -g -ggdb   -pedantic hiredis.c
cc -std=c99 -c -O0 -fPIC   -Wall -Wextra -Werror -Wstrict-prototypes -Wwrite-strings -Wno-missing-field-initializers -g -ggdb   -pedantic sds.c
cc -std=c99 -c -O0 -fPIC   -Wall -Wextra -Werror -Wstrict-prototypes -Wwrite-strings -Wno-missing-field-initializers -g -ggdb   -pedantic async.c
cc -std=c99 -c -O0 -fPIC   -Wall -Wextra -Werror -Wstrict-prototypes -Wwrite-strings -Wno-missing-field-initializers -g -ggdb   -pedantic read.c
cc -std=c99 -c -O0 -fPIC   -Wall -Wextra -Werror -Wstrict-prototypes -Wwrite-strings -Wno-missing-field-initializers -g -ggdb   -pedantic sockcompat.c
ar rcs libhiredis.a alloc.o net.o hiredis.o sds.o async.o read.o sockcompat.o
MAKE linenoise
cd linenoise && /Applications/Xcode.app/Contents/Developer/usr/bin/make CFLAGS="" LDFLAGS=""
cc  -Wall -Os -g  -c linenoise.c
MAKE lua
cd lua/src && /Applications/Xcode.app/Contents/Developer/usr/bin/make all CFLAGS="-Wall -DLUA_ANSI -DENABLE_CJSON_GLOBAL -DREDIS_STATIC='' -DLUA_USE_MKSTEMP  -O2 " MYLDFLAGS="" AR="ar rc"
cc -Wall -DLUA_ANSI -DENABLE_CJSON_GLOBAL -DREDIS_STATIC='' -DLUA_USE_MKSTEMP  -O2    -c -o lapi.o lapi.c
cc -Wall -DLUA_ANSI -DENABLE_CJSON_GLOBAL -DREDIS_STATIC='' -DLUA_USE_MKSTEMP  -O2    -c -o lcode.o lcode.c
cc -Wall -DLUA_ANSI -DENABLE_CJSON_GLOBAL -DREDIS_STATIC='' -DLUA_USE_MKSTEMP  -O2    -c -o ldebug.o ldebug.c
cc -Wall -DLUA_ANSI -DENABLE_CJSON_GLOBAL -DREDIS_STATIC='' -DLUA_USE_MKSTEMP  -O2    -c -o ldo.o ldo.c
cc -Wall -DLUA_ANSI -DENABLE_CJSON_GLOBAL -DREDIS_STATIC='' -DLUA_USE_MKSTEMP  -O2    -c -o ldump.o ldump.c
cc -Wall -DLUA_ANSI -DENABLE_CJSON_GLOBAL -DREDIS_STATIC='' -DLUA_USE_MKSTEMP  -O2    -c -o lfunc.o lfunc.c
cc -Wall -DLUA_ANSI -DENABLE_CJSON_GLOBAL -DREDIS_STATIC='' -DLUA_USE_MKSTEMP  -O2    -c -o lgc.o lgc.c
cc -Wall -DLUA_ANSI -DENABLE_CJSON_GLOBAL -DREDIS_STATIC='' -DLUA_USE_MKSTEMP  -O2    -c -o llex.o llex.c
cc -Wall -DLUA_ANSI -DENABLE_CJSON_GLOBAL -DREDIS_STATIC='' -DLUA_USE_MKSTEMP  -O2    -c -o lmem.o lmem.c
cc -Wall -DLUA_ANSI -DENABLE_CJSON_GLOBAL -DREDIS_STATIC='' -DLUA_USE_MKSTEMP  -O2    -c -o lobject.o lobject.c
cc -Wall -DLUA_ANSI -DENABLE_CJSON_GLOBAL -DREDIS_STATIC='' -DLUA_USE_MKSTEMP  -O2    -c -o lopcodes.o lopcodes.c
cc -Wall -DLUA_ANSI -DENABLE_CJSON_GLOBAL -DREDIS_STATIC='' -DLUA_USE_MKSTEMP  -O2    -c -o lparser.o lparser.c
cc -Wall -DLUA_ANSI -DENABLE_CJSON_GLOBAL -DREDIS_STATIC='' -DLUA_USE_MKSTEMP  -O2    -c -o lstate.o lstate.c
cc -Wall -DLUA_ANSI -DENABLE_CJSON_GLOBAL -DREDIS_STATIC='' -DLUA_USE_MKSTEMP  -O2    -c -o lstring.o lstring.c
cc -Wall -DLUA_ANSI -DENABLE_CJSON_GLOBAL -DREDIS_STATIC='' -DLUA_USE_MKSTEMP  -O2    -c -o ltable.o ltable.c
cc -Wall -DLUA_ANSI -DENABLE_CJSON_GLOBAL -DREDIS_STATIC='' -DLUA_USE_MKSTEMP  -O2    -c -o ltm.o ltm.c
cc -Wall -DLUA_ANSI -DENABLE_CJSON_GLOBAL -DREDIS_STATIC='' -DLUA_USE_MKSTEMP  -O2    -c -o lundump.o lundump.c
cc -Wall -DLUA_ANSI -DENABLE_CJSON_GLOBAL -DREDIS_STATIC='' -DLUA_USE_MKSTEMP  -O2    -c -o lvm.o lvm.c
cc -Wall -DLUA_ANSI -DENABLE_CJSON_GLOBAL -DREDIS_STATIC='' -DLUA_USE_MKSTEMP  -O2    -c -o lzio.o lzio.c
cc -Wall -DLUA_ANSI -DENABLE_CJSON_GLOBAL -DREDIS_STATIC='' -DLUA_USE_MKSTEMP  -O2    -c -o strbuf.o strbuf.c
cc -Wall -DLUA_ANSI -DENABLE_CJSON_GLOBAL -DREDIS_STATIC='' -DLUA_USE_MKSTEMP  -O2    -c -o fpconv.o fpconv.c
cc -Wall -DLUA_ANSI -DENABLE_CJSON_GLOBAL -DREDIS_STATIC='' -DLUA_USE_MKSTEMP  -O2    -c -o lauxlib.o lauxlib.c
cc -Wall -DLUA_ANSI -DENABLE_CJSON_GLOBAL -DREDIS_STATIC='' -DLUA_USE_MKSTEMP  -O2    -c -o lbaselib.o lbaselib.c
cc -Wall -DLUA_ANSI -DENABLE_CJSON_GLOBAL -DREDIS_STATIC='' -DLUA_USE_MKSTEMP  -O2    -c -o ldblib.o ldblib.c
cc -Wall -DLUA_ANSI -DENABLE_CJSON_GLOBAL -DREDIS_STATIC='' -DLUA_USE_MKSTEMP  -O2    -c -o liolib.o liolib.c
cc -Wall -DLUA_ANSI -DENABLE_CJSON_GLOBAL -DREDIS_STATIC='' -DLUA_USE_MKSTEMP  -O2    -c -o lmathlib.o lmathlib.c
cc -Wall -DLUA_ANSI -DENABLE_CJSON_GLOBAL -DREDIS_STATIC='' -DLUA_USE_MKSTEMP  -O2    -c -o loslib.o loslib.c
cc -Wall -DLUA_ANSI -DENABLE_CJSON_GLOBAL -DREDIS_STATIC='' -DLUA_USE_MKSTEMP  -O2    -c -o ltablib.o ltablib.c
cc -Wall -DLUA_ANSI -DENABLE_CJSON_GLOBAL -DREDIS_STATIC='' -DLUA_USE_MKSTEMP  -O2    -c -o lstrlib.o lstrlib.c
cc -Wall -DLUA_ANSI -DENABLE_CJSON_GLOBAL -DREDIS_STATIC='' -DLUA_USE_MKSTEMP  -O2    -c -o loadlib.o loadlib.c
cc -Wall -DLUA_ANSI -DENABLE_CJSON_GLOBAL -DREDIS_STATIC='' -DLUA_USE_MKSTEMP  -O2    -c -o linit.o linit.c
cc -Wall -DLUA_ANSI -DENABLE_CJSON_GLOBAL -DREDIS_STATIC='' -DLUA_USE_MKSTEMP  -O2    -c -o lua_cjson.o lua_cjson.c
cc -Wall -DLUA_ANSI -DENABLE_CJSON_GLOBAL -DREDIS_STATIC='' -DLUA_USE_MKSTEMP  -O2    -c -o lua_struct.o lua_struct.c
cc -Wall -DLUA_ANSI -DENABLE_CJSON_GLOBAL -DREDIS_STATIC='' -DLUA_USE_MKSTEMP  -O2    -c -o lua_cmsgpack.o lua_cmsgpack.c
cc -Wall -DLUA_ANSI -DENABLE_CJSON_GLOBAL -DREDIS_STATIC='' -DLUA_USE_MKSTEMP  -O2    -c -o lua_bit.o lua_bit.c
ar rc liblua.a lapi.o lcode.o ldebug.o ldo.o ldump.o lfunc.o lgc.o llex.o lmem.o lobject.o lopcodes.o lparser.o lstate.o lstring.o ltable.o ltm.o lundump.o lvm.o lzio.o strbuf.o fpconv.o lauxlib.o lbaselib.o ldblib.o liolib.o lmathlib.o loslib.o ltablib.o lstrlib.o loadlib.o linit.o lua_cjson.o lua_struct.o lua_cmsgpack.o lua_bit.o       # DLL needs all object files
ranlib liblua.a
cc -Wall -DLUA_ANSI -DENABLE_CJSON_GLOBAL -DREDIS_STATIC='' -DLUA_USE_MKSTEMP  -O2    -c -o lua.o lua.c
cc -o lua  lua.o liblua.a -lm 
cc -Wall -DLUA_ANSI -DENABLE_CJSON_GLOBAL -DREDIS_STATIC='' -DLUA_USE_MKSTEMP  -O2    -c -o luac.o luac.c
cc -Wall -DLUA_ANSI -DENABLE_CJSON_GLOBAL -DREDIS_STATIC='' -DLUA_USE_MKSTEMP  -O2    -c -o print.o print.c
cc -o luac  luac.o print.o liblua.a -lm 
MAKE hdr_histogram
cd hdr_histogram && /Applications/Xcode.app/Contents/Developer/usr/bin/make CFLAGS="" LDFLAGS=""
cc -std=c99 -Wall -Os -g  -DHDR_MALLOC_INCLUDE=\"hdr_redis_malloc.h\" -c  hdr_histogram.c 
ar rcs libhdrhistogram.a hdr_histogram.o
MAKE fpconv
cd fpconv && /Applications/Xcode.app/Contents/Developer/usr/bin/make CFLAGS="" LDFLAGS=""
cc  -Wall -Os -g  -c  fpconv_dtoa.c 
ar rcs libfpconv.a fpconv_dtoa.o
MAKE fast_float
cd fast_float && /Applications/Xcode.app/Contents/Developer/usr/bin/make libfast_float CFLAGS="" LDFLAGS=""
c++ -Wall -O3 -std=c++11 -DFASTFLOAT_ALLOWS_LEADING_PLUS  -c fast_float_strtod.cpp 
ar -r libfast_float.a fast_float_strtod.o
ar: creating archive libfast_float.a
MAKE xxhash
cd xxhash && /Applications/Xcode.app/Contents/Developer/usr/bin/make lib CFLAGS="-fPIC " LDFLAGS=""
CC cachedObjs/cbad4ce87f68cd06aa92ff37a641d079/xxhash.o
AR cachedObjs/cbad4ce87f68cd06aa92ff37a641d079/libxxhash.a
CC cachedObjs/7ec56b87b019ae6787084253027bf7f8/xxhash.o
LD cachedObjs/7ec56b87b019ae6787084253027bf7f8/libxxhash.0.8.3.dylib
    CC threads_mngr.o
    CC memory_prefetch.o
    CC adlist.o
    CC quicklist.o
    CC ae.o
    CC anet.o
    CC dict.o
    CC ebuckets.o
    CC eventnotifier.o
    CC iothread.o
    CC mstr.o
    CC kvstore.o
    CC fwtree.o
    CC estore.o
    CC server.o
    CC sds.o
    CC zmalloc.o
    CC lzf_c.o
    CC lzf_d.o
    CC pqsort.o
    CC zipmap.o
    CC sha1.o
    CC ziplist.o
    CC release.o
    CC networking.o
    CC util.o
    CC object.o
    CC db.o
    CC replication.o
    CC rdb.o
    CC t_string.o
    CC t_list.o
    CC t_set.o
    CC t_zset.o
    CC t_hash.o
    CC config.o
    CC aof.o
    CC pubsub.o
    CC multi.o
    CC debug.o
    CC sort.o
    CC intset.o
    CC syncio.o
    CC cluster.o
    CC cluster_asm.o
    CC cluster_legacy.o
    CC cluster_slot_stats.o
    CC crc16.o
    CC endianconv.o
    CC slowlog.o
    CC eval.o
    CC bio.o
    CC rio.o
    CC rand.o
    CC memtest.o
    CC syscheck.o
    CC crcspeed.o
    CC crccombine.o
    CC crc64.o
    CC bitops.o
    CC sentinel.o
    CC notify.o
    CC setproctitle.o
    CC blocked.o
    CC hyperloglog.o
    CC latency.o
    CC sparkline.o
    CC redis-check-rdb.o
    CC redis-check-aof.o
    CC geo.o
    CC lazyfree.o
    CC module.o
    CC evict.o
    CC expire.o
    CC geohash.o
    CC geohash_helper.o
    CC childinfo.o
    CC defrag.o
    CC siphash.o
    CC rax.o
    CC t_stream.o
    CC listpack.o
    CC localtime.o
    CC lolwut.o
    CC lolwut5.o
    CC lolwut6.o
    CC lolwut8.o
    CC acl.o
    CC tracking.o
    CC socket.o
    CC tls.o
    CC sha256.o
    CC timeout.o
    CC setcpuaffinity.o
    CC monotonic.o
    CC mt19937-64.o
    CC resp_parser.o
    CC call_reply.o
    CC script_lua.o
    CC script.o
    CC functions.o
    CC function_lua.o
    CC commands.o
    CC strl.o
    CC connection.o
    CC unix.o
    CC logreqres.o
    CC hnsw.o
    CC vset.o
    CC vset_config.o
    LINK redis-server
    INSTALL redis-sentinel
    CC redis-cli.o
    CC redisassert.o
    CC cli_common.o
    CC cli_commands.o
    LINK redis-cli
    CC redis-benchmark.o
    LINK redis-benchmark
    INSTALL redis-check-rdb
    INSTALL redis-check-aof
/Applications/Xcode.app/Contents/Developer/usr/bin/make -C ../tests/modules
cc -I../../src  -W -Wall -Wno-missing-field-initializers -dynamic -fno-common -g -ggdb -std=gnu11 -O2 -fPIC -c commandfilter.c -o commandfilter.xo
ld -o commandfilter.so commandfilter.xo -bundle -undefined dynamic_lookup  -L /Library/Developer/CommandLineTools/SDKs/MacOSX.sdk/usr/lib -lsystem
cc -I../../src  -W -Wall -Wno-missing-field-initializers -dynamic -fno-common -g -ggdb -std=gnu11 -O2 -fPIC -c basics.c -o basics.xo
ld -o basics.so basics.xo -bundle -undefined dynamic_lookup  -L /Library/Developer/CommandLineTools/SDKs/MacOSX.sdk/usr/lib -lsystem
cc -I../../src  -W -Wall -Wno-missing-field-initializers -dynamic -fno-common -g -ggdb -std=gnu11 -O2 -fPIC -c testrdb.c -o testrdb.xo
ld -o testrdb.so testrdb.xo -bundle -undefined dynamic_lookup  -L /Library/Developer/CommandLineTools/SDKs/MacOSX.sdk/usr/lib -lsystem
cc -I../../src  -W -Wall -Wno-missing-field-initializers -dynamic -fno-common -g -ggdb -std=gnu11 -O2 -fPIC -c fork.c -o fork.xo
ld -o fork.so fork.xo -bundle -undefined dynamic_lookup  -L /Library/Developer/CommandLineTools/SDKs/MacOSX.sdk/usr/lib -lsystem
cc -I../../src  -W -Wall -Wno-missing-field-initializers -dynamic -fno-common -g -ggdb -std=gnu11 -O2 -fPIC -c infotest.c -o infotest.xo
ld -o infotest.so infotest.xo -bundle -undefined dynamic_lookup  -L /Library/Developer/CommandLineTools/SDKs/MacOSX.sdk/usr/lib -lsystem
cc -I../../src  -W -Wall -Wno-missing-field-initializers -dynamic -fno-common -g -ggdb -std=gnu11 -O2 -fPIC -c propagate.c -o propagate.xo
ld -o propagate.so propagate.xo -bundle -undefined dynamic_lookup  -L /Library/Developer/CommandLineTools/SDKs/MacOSX.sdk/usr/lib -lsystem
cc -I../../src  -W -Wall -Wno-missing-field-initializers -dynamic -fno-common -g -ggdb -std=gnu11 -O2 -fPIC -c misc.c -o misc.xo
ld -o misc.so misc.xo -bundle -undefined dynamic_lookup  -L /Library/Developer/CommandLineTools/SDKs/MacOSX.sdk/usr/lib -lsystem
cc -I../../src  -W -Wall -Wno-missing-field-initializers -dynamic -fno-common -g -ggdb -std=gnu11 -O2 -fPIC -c hooks.c -o hooks.xo
ld -o hooks.so hooks.xo -bundle -undefined dynamic_lookup  -L /Library/Developer/CommandLineTools/SDKs/MacOSX.sdk/usr/lib -lsystem
cc -I../../src  -W -Wall -Wno-missing-field-initializers -dynamic -fno-common -g -ggdb -std=gnu11 -O2 -fPIC -c blockonkeys.c -o blockonkeys.xo
ld -o blockonkeys.so blockonkeys.xo -bundle -undefined dynamic_lookup  -L /Library/Developer/CommandLineTools/SDKs/MacOSX.sdk/usr/lib -lsystem
cc -I../../src  -W -Wall -Wno-missing-field-initializers -dynamic -fno-common -g -ggdb -std=gnu11 -O2 -fPIC -c blockonbackground.c -o blockonbackground.xo
ld -o blockonbackground.so blockonbackground.xo -bundle -undefined dynamic_lookup  -L /Library/Developer/CommandLineTools/SDKs/MacOSX.sdk/usr/lib -lsystem
cc -I../../src  -W -Wall -Wno-missing-field-initializers -dynamic -fno-common -g -ggdb -std=gnu11 -O2 -fPIC -c scan.c -o scan.xo
ld -o scan.so scan.xo -bundle -undefined dynamic_lookup  -L /Library/Developer/CommandLineTools/SDKs/MacOSX.sdk/usr/lib -lsystem
cc -I../../src  -W -Wall -Wno-missing-field-initializers -dynamic -fno-common -g -ggdb -std=gnu11 -O2 -fPIC -c datatype.c -o datatype.xo
ld -o datatype.so datatype.xo -bundle -undefined dynamic_lookup  -L /Library/Developer/CommandLineTools/SDKs/MacOSX.sdk/usr/lib -lsystem
cc -I../../src  -W -Wall -Wno-missing-field-initializers -dynamic -fno-common -g -ggdb -std=gnu11 -O2 -fPIC -c datatype2.c -o datatype2.xo
ld -o datatype2.so datatype2.xo -bundle -undefined dynamic_lookup  -L /Library/Developer/CommandLineTools/SDKs/MacOSX.sdk/usr/lib -lsystem
cc -I../../src  -W -Wall -Wno-missing-field-initializers -dynamic -fno-common -g -ggdb -std=gnu11 -O2 -fPIC -c auth.c -o auth.xo
ld -o auth.so auth.xo -bundle -undefined dynamic_lookup  -L /Library/Developer/CommandLineTools/SDKs/MacOSX.sdk/usr/lib -lsystem
cc -I../../src  -W -Wall -Wno-missing-field-initializers -dynamic -fno-common -g -ggdb -std=gnu11 -O2 -fPIC -c keyspace_events.c -o keyspace_events.xo
ld -o keyspace_events.so keyspace_events.xo -bundle -undefined dynamic_lookup  -L /Library/Developer/CommandLineTools/SDKs/MacOSX.sdk/usr/lib -lsystem
cc -I../../src  -W -Wall -Wno-missing-field-initializers -dynamic -fno-common -g -ggdb -std=gnu11 -O2 -fPIC -c blockedclient.c -o blockedclient.xo
ld -o blockedclient.so blockedclient.xo -bundle -undefined dynamic_lookup  -L /Library/Developer/CommandLineTools/SDKs/MacOSX.sdk/usr/lib -lsystem
cc -I../../src  -W -Wall -Wno-missing-field-initializers -dynamic -fno-common -g -ggdb -std=gnu11 -O2 -fPIC -c getkeys.c -o getkeys.xo
ld -o getkeys.so getkeys.xo -bundle -undefined dynamic_lookup  -L /Library/Developer/CommandLineTools/SDKs/MacOSX.sdk/usr/lib -lsystem
cc -I../../src  -W -Wall -Wno-missing-field-initializers -dynamic -fno-common -g -ggdb -std=gnu11 -O2 -fPIC -c getchannels.c -o getchannels.xo
ld -o getchannels.so getchannels.xo -bundle -undefined dynamic_lookup  -L /Library/Developer/CommandLineTools/SDKs/MacOSX.sdk/usr/lib -lsystem
cc -I../../src  -W -Wall -Wno-missing-field-initializers -dynamic -fno-common -g -ggdb -std=gnu11 -O2 -fPIC -c test_lazyfree.c -o test_lazyfree.xo
ld -o test_lazyfree.so test_lazyfree.xo -bundle -undefined dynamic_lookup  -L /Library/Developer/CommandLineTools/SDKs/MacOSX.sdk/usr/lib -lsystem
cc -I../../src  -W -Wall -Wno-missing-field-initializers -dynamic -fno-common -g -ggdb -std=gnu11 -O2 -fPIC -c timer.c -o timer.xo
ld -o timer.so timer.xo -bundle -undefined dynamic_lookup  -L /Library/Developer/CommandLineTools/SDKs/MacOSX.sdk/usr/lib -lsystem
cc -I../../src  -W -Wall -Wno-missing-field-initializers -dynamic -fno-common -g -ggdb -std=gnu11 -O2 -fPIC -c defragtest.c -o defragtest.xo
ld -o defragtest.so defragtest.xo -bundle -undefined dynamic_lookup  -L /Library/Developer/CommandLineTools/SDKs/MacOSX.sdk/usr/lib -lsystem
cc -I../../src  -W -Wall -Wno-missing-field-initializers -dynamic -fno-common -g -ggdb -std=gnu11 -O2 -fPIC -c keyspecs.c -o keyspecs.xo
ld -o keyspecs.so keyspecs.xo -bundle -undefined dynamic_lookup  -L /Library/Developer/CommandLineTools/SDKs/MacOSX.sdk/usr/lib -lsystem
cc -I../../src  -W -Wall -Wno-missing-field-initializers -dynamic -fno-common -g -ggdb -std=gnu11 -O2 -fPIC -c hash.c -o hash.xo
ld -o hash.so hash.xo -bundle -undefined dynamic_lookup  -L /Library/Developer/CommandLineTools/SDKs/MacOSX.sdk/usr/lib -lsystem
cc -I../../src  -W -Wall -Wno-missing-field-initializers -dynamic -fno-common -g -ggdb -std=gnu11 -O2 -fPIC -c zset.c -o zset.xo
ld -o zset.so zset.xo -bundle -undefined dynamic_lookup  -L /Library/Developer/CommandLineTools/SDKs/MacOSX.sdk/usr/lib -lsystem
cc -I../../src  -W -Wall -Wno-missing-field-initializers -dynamic -fno-common -g -ggdb -std=gnu11 -O2 -fPIC -c stream.c -o stream.xo
ld -o stream.so stream.xo -bundle -undefined dynamic_lookup  -L /Library/Developer/CommandLineTools/SDKs/MacOSX.sdk/usr/lib -lsystem
cc -I../../src  -W -Wall -Wno-missing-field-initializers -dynamic -fno-common -g -ggdb -std=gnu11 -O2 -fPIC -c mallocsize.c -o mallocsize.xo
ld -o mallocsize.so mallocsize.xo -bundle -undefined dynamic_lookup  -L /Library/Developer/CommandLineTools/SDKs/MacOSX.sdk/usr/lib -lsystem
cc -I../../src  -W -Wall -Wno-missing-field-initializers -dynamic -fno-common -g -ggdb -std=gnu11 -O2 -fPIC -c aclcheck.c -o aclcheck.xo
ld -o aclcheck.so aclcheck.xo -bundle -undefined dynamic_lookup  -L /Library/Developer/CommandLineTools/SDKs/MacOSX.sdk/usr/lib -lsystem
cc -I../../src  -W -Wall -Wno-missing-field-initializers -dynamic -fno-common -g -ggdb -std=gnu11 -O2 -fPIC -c list.c -o list.xo
ld -o list.so list.xo -bundle -undefined dynamic_lookup  -L /Library/Developer/CommandLineTools/SDKs/MacOSX.sdk/usr/lib -lsystem
cc -I../../src  -W -Wall -Wno-missing-field-initializers -dynamic -fno-common -g -ggdb -std=gnu11 -O2 -fPIC -c subcommands.c -o subcommands.xo
ld -o subcommands.so subcommands.xo -bundle -undefined dynamic_lookup  -L /Library/Developer/CommandLineTools/SDKs/MacOSX.sdk/usr/lib -lsystem
cc -I../../src  -W -Wall -Wno-missing-field-initializers -dynamic -fno-common -g -ggdb -std=gnu11 -O2 -fPIC -c reply.c -o reply.xo
ld -o reply.so reply.xo -bundle -undefined dynamic_lookup  -L /Library/Developer/CommandLineTools/SDKs/MacOSX.sdk/usr/lib -lsystem
cc -I../../src  -W -Wall -Wno-missing-field-initializers -dynamic -fno-common -g -ggdb -std=gnu11 -O2 -fPIC -c cmdintrospection.c -o cmdintrospection.xo
ld -o cmdintrospection.so cmdintrospection.xo -bundle -undefined dynamic_lookup  -L /Library/Developer/CommandLineTools/SDKs/MacOSX.sdk/usr/lib -lsystem
cc -I../../src  -W -Wall -Wno-missing-field-initializers -dynamic -fno-common -g -ggdb -std=gnu11 -O2 -fPIC -c eventloop.c -o eventloop.xo
ld -o eventloop.so eventloop.xo -bundle -undefined dynamic_lookup  -L /Library/Developer/CommandLineTools/SDKs/MacOSX.sdk/usr/lib -lsystem
cc -I../../src  -W -Wall -Wno-missing-field-initializers -dynamic -fno-common -g -ggdb -std=gnu11 -O2 -fPIC -c moduleconfigs.c -o moduleconfigs.xo
ld -o moduleconfigs.so moduleconfigs.xo -bundle -undefined dynamic_lookup  -L /Library/Developer/CommandLineTools/SDKs/MacOSX.sdk/usr/lib -lsystem
cc -I../../src  -W -Wall -Wno-missing-field-initializers -dynamic -fno-common -g -ggdb -std=gnu11 -O2 -fPIC -c moduleconfigstwo.c -o moduleconfigstwo.xo
ld -o moduleconfigstwo.so moduleconfigstwo.xo -bundle -undefined dynamic_lookup  -L /Library/Developer/CommandLineTools/SDKs/MacOSX.sdk/usr/lib -lsystem
cc -I../../src  -W -Wall -Wno-missing-field-initializers -dynamic -fno-common -g -ggdb -std=gnu11 -O2 -fPIC -c publish.c -o publish.xo
ld -o publish.so publish.xo -bundle -undefined dynamic_lookup  -L /Library/Developer/CommandLineTools/SDKs/MacOSX.sdk/usr/lib -lsystem
cc -I../../src  -W -Wall -Wno-missing-field-initializers -dynamic -fno-common -g -ggdb -std=gnu11 -O2 -fPIC -c usercall.c -o usercall.xo
ld -o usercall.so usercall.xo -bundle -undefined dynamic_lookup  -L /Library/Developer/CommandLineTools/SDKs/MacOSX.sdk/usr/lib -lsystem
cc -I../../src  -W -Wall -Wno-missing-field-initializers -dynamic -fno-common -g -ggdb -std=gnu11 -O2 -fPIC -c postnotifications.c -o postnotifications.xo
ld -o postnotifications.so postnotifications.xo -bundle -undefined dynamic_lookup  -L /Library/Developer/CommandLineTools/SDKs/MacOSX.sdk/usr/lib -lsystem
cc -I../../src  -W -Wall -Wno-missing-field-initializers -dynamic -fno-common -g -ggdb -std=gnu11 -O2 -fPIC -c moduleauthtwo.c -o moduleauthtwo.xo
ld -o moduleauthtwo.so moduleauthtwo.xo -bundle -undefined dynamic_lookup  -L /Library/Developer/CommandLineTools/SDKs/MacOSX.sdk/usr/lib -lsystem
cc -I../../src  -W -Wall -Wno-missing-field-initializers -dynamic -fno-common -g -ggdb -std=gnu11 -O2 -fPIC -c rdbloadsave.c -o rdbloadsave.xo
ld -o rdbloadsave.so rdbloadsave.xo -bundle -undefined dynamic_lookup  -L /Library/Developer/CommandLineTools/SDKs/MacOSX.sdk/usr/lib -lsystem
cc -I../../src  -W -Wall -Wno-missing-field-initializers -dynamic -fno-common -g -ggdb -std=gnu11 -O2 -fPIC -c crash.c -o crash.xo
ld -o crash.so crash.xo -bundle -undefined dynamic_lookup  -L /Library/Developer/CommandLineTools/SDKs/MacOSX.sdk/usr/lib -lsystem
cc -I../../src  -W -Wall -Wno-missing-field-initializers -dynamic -fno-common -g -ggdb -std=gnu11 -O2 -fPIC -c internalsecret.c -o internalsecret.xo
ld -o internalsecret.so internalsecret.xo -bundle -undefined dynamic_lookup  -L /Library/Developer/CommandLineTools/SDKs/MacOSX.sdk/usr/lib -lsystem
cc -I../../src  -W -Wall -Wno-missing-field-initializers -dynamic -fno-common -g -ggdb -std=gnu11 -O2 -fPIC -c configaccess.c -o configaccess.xo
ld -o configaccess.so configaccess.xo -bundle -undefined dynamic_lookup  -L /Library/Developer/CommandLineTools/SDKs/MacOSX.sdk/usr/lib -lsystem
cc -I../../src  -W -Wall -Wno-missing-field-initializers -dynamic -fno-common -g -ggdb -std=gnu11 -O2 -fPIC -c atomicslotmigration.c -o atomicslotmigration.xo
ld -o atomicslotmigration.so atomicslotmigration.xo -bundle -undefined dynamic_lookup  -L /Library/Developer/CommandLineTools/SDKs/MacOSX.sdk/usr/lib -lsystem
rm moduleauthtwo.xo blockedclient.xo fork.xo datatype2.xo auth.xo publish.xo subcommands.xo keyspace_events.xo getkeys.xo datatype.xo list.xo blockonkeys.xo reply.xo cmdintrospection.xo hash.xo hooks.xo timer.xo rdbloadsave.xo infotest.xo eventloop.xo moduleconfigs.xo testrdb.xo configaccess.xo commandfilter.xo getchannels.xo keyspecs.xo postnotifications.xo usercall.xo defragtest.xo stream.xo internalsecret.xo basics.xo scan.xo test_lazyfree.xo atomicslotmigration.xo crash.xo zset.xo mallocsize.xo moduleconfigstwo.xo blockonbackground.xo misc.xo propagate.xo aclcheck.xo

Hint: It's a good idea to run 'make test' ;)


    CC Makefile.dep
    CC Makefile.dep
nv) ➜  redis git:(feature/1.0) ✗ ll src/redis-server
-rwxr-xr-x@ 1 huoyinghui  staff   3.2M 10 27 22:46 src/redis-server
(venv) ➜  redis git:(feature/1.0) ✗ 
```