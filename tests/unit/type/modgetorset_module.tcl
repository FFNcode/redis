start_server {tags {"modgetorset_module"}} {
    # 加载模块
    # r MODULE LOAD /Users/admin/Downloads/test/github/redis-unstable/modules/modgetorset/modgetorset.so
    test {MOD_GET_OR_SET sets value when key does not exist} {
        set result [r MOD_GET_OR_SET counter 0]
        assert_equal $result "0"
    }

    test {MOD_GET_OR_SET returns existing value} {
        r SET counter 10
        set result [r MOD_GET_OR_SET counter 0]
        assert_equal $result "10"
    }

    
    # 卸载模块
    #r MODULE UNLOAD modgetorset
}