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