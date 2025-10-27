## make build

```
/redis-server: Mach-O 64-bit executable arm64
➜  redis git:(feature/1.0) ✗ ./src/redis-server 
65967:C 22 Oct 2025 22:28:21.014 * oO0OoO0OoO0Oo Redis is starting oO0OoO0OoO0Oo
65967:C 22 Oct 2025 22:28:21.014 * Redis version=255.255.255, bits=64, commit=2bc4e029, modified=0, pid=65967, just started
65967:C 22 Oct 2025 22:28:21.014 # Warning: no config file specified, using the default config. In order to specify a config file use ./src/redis-server /path/to/redis.conf
65967:M 22 Oct 2025 22:28:21.015 * monotonic clock: POSIX clock_gettime
                _._                                                  
           _.-``__ ''-._                                             
      _.-``    `.  `_.  ''-._           Redis Open Source            
  .-`` .-```.  ```\/    _.,_ ''-._      255.255.255 (2bc4e029/0) 64 bit
 (    '      ,       .-`  | `,    )     Running in standalone mode
 |`-._`-...-` __...-.``-._|'` _.-'|     Port: 6379
 |    `-._   `._    /     _.-'    |     PID: 65967
  `-._    `-._  `-./  _.-'    _.-'                                   
 |`-._`-._    `-.__.-'    _.-'_.-'|                                  
 |    `-._`-._        _.-'_.-'    |           https://redis.io       
  `-._    `-._`-.__.-'_.-'    _.-'                                   
 |`-._`-._    `-.__.-'    _.-'_.-'|                                  
 |    `-._`-._        _.-'_.-'    |                                  
  `-._    `-._`-.__.-'_.-'    _.-'                                   
      `-._    `-.__.-'    _.-'                                       
          `-._        _.-'                                           
              `-.__.-'                                               

65967:M 22 Oct 2025 22:28:21.015 # WARNING: The TCP backlog setting of 511 cannot be enforced because kern.ipc.somaxconn is set to the lower value of 128.
65967:M 22 Oct 2025 22:28:21.016 * Server initialized
65967:M 22 Oct 2025 22:28:21.016 * Ready to accept connections tcp

```


## 所有模块
```
➜  redis git:(feature/1.0) make BUILD_WITH_MODULES=yes
```

## make install 

```shell
make install # 安装在 /usr/local/bin/redis-server
make install PREFIX=./bin/
```

```shell
redis git:(feature/1.0) ✗ make install PREFIX=./bin/
for dir in src; do /Applications/Xcode.app/Contents/Developer/usr/bin/make -C $dir install; done
/Applications/Xcode.app/Contents/Developer/usr/bin/make -C ../tests/modules
make[2]: Nothing to be done for `all'.

Hint: It's a good idea to run 'make test' ;)

    INSTALL redis-server
    INSTALL redis-benchmark
    INSTALL redis-cli
➜  redis git:(feature/1.0) ✗ 
```

## clion debug
```

(venv) ➜  redis git:(feature/1.0) ✗ make clean
for dir in src; do /Applications/Xcode.app/Contents/Developer/usr/bin/make -C $dir clean; done
rm -rf redis-server redis-sentinel redis-cli redis-benchmark redis-check-rdb redis-check-aof *.o *.gcda *.gcno *.gcov redis.info lcov-html Makefile.dep *.so
rm -f threads_mngr.d memory_prefetch.d adlist.d quicklist.d ae.d anet.d dict.d ebuckets.d eventnotifier.d iothread.d mstr.d kvstore.d fwtree.d estore.d server.d sds.d zmalloc.d lzf_c.d lzf_d.d pqsort.d zipmap.d sha1.d ziplist.d release.d networking.d util.d object.d db.d replication.d rdb.d t_string.d t_list.d t_set.d t_zset.d t_hash.d config.d aof.d pubsub.d multi.d debug.d sort.d intset.d syncio.d cluster.d cluster_asm.d cluster_legacy.d cluster_slot_stats.d crc16.d endianconv.d slowlog.d eval.d bio.d rio.d rand.d memtest.d syscheck.d crcspeed.d crccombine.d crc64.d bitops.d sentinel.d notify.d setproctitle.d blocked.d hyperloglog.d latency.d sparkline.d redis-check-rdb.d redis-check-aof.d geo.d lazyfree.d module.d evict.d expire.d geohash.d geohash_helper.d childinfo.d defrag.d siphash.d rax.d t_stream.d listpack.d localtime.d lolwut.d lolwut5.d lolwut6.d lolwut8.d acl.d tracking.d socket.d tls.d sha256.d timeout.d setcpuaffinity.d monotonic.d mt19937-64.d resp_parser.d call_reply.d script_lua.d script.d functions.d function_lua.d commands.d strl.d connection.d unix.d logreqres.d hnsw.d vset.d vset_config.d anet.d adlist.d dict.d redis-cli.d zmalloc.d release.d ae.d redisassert.d crcspeed.d crccombine.d crc64.d siphash.d crc16.d monotonic.d cli_common.d mt19937-64.d strl.d cli_commands.d ae.d anet.d redis-benchmark.d adlist.d dict.d zmalloc.d redisassert.d release.d crcspeed.d crccombine.d crc64.d siphash.d crc16.d monotonic.d cli_common.d mt19937-64.d strl.d
(cd ../tests/modules && /Applications/Xcode.app/Contents/Developer/usr/bin/make clean)
rm -f commandfilter.so basics.so testrdb.so fork.so infotest.so propagate.so misc.so hooks.so blockonkeys.so blockonbackground.so scan.so datatype.so datatype2.so auth.so keyspace_events.so blockedclient.so getkeys.so getchannels.so test_lazyfree.so timer.so defragtest.so keyspecs.so hash.so zset.so stream.so mallocsize.so aclcheck.so list.so subcommands.so reply.so cmdintrospection.so eventloop.so moduleconfigs.so moduleconfigstwo.so publish.so usercall.so postnotifications.so moduleauthtwo.so rdbloadsave.so crash.so internalsecret.so configaccess.so atomicslotmigration.so commandfilter.xo basics.xo testrdb.xo fork.xo infotest.xo propagate.xo misc.xo hooks.xo blockonkeys.xo blockonbackground.xo scan.xo datatype.xo datatype2.xo auth.xo keyspace_events.xo blockedclient.xo getkeys.xo getchannels.xo test_lazyfree.xo timer.xo defragtest.xo keyspecs.xo hash.xo zset.xo stream.xo mallocsize.xo aclcheck.xo list.xo subcommands.xo reply.xo cmdintrospection.xo eventloop.xo moduleconfigs.xo moduleconfigstwo.xo publish.xo usercall.xo postnotifications.xo moduleauthtwo.xo rdbloadsave.xo crash.xo internalsecret.xo configaccess.xo atomicslotmigration.xo
(venv) ➜  redis git:(feature/1.0) ✗ rm -rf src/.make-settings 
(venv) ➜  redis git:(feature/1.0) ✗ compiledb -nf make OPTIMIZATION=-O0
    CC Makefile.dep
    CC Makefile.dep
(venv) ➜  redis git:(feature/1.0) ✗ 
```