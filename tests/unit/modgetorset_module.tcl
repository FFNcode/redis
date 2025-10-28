set testmodule [file normalize modules/modgetorset/modgetorset.so]

start_server {tags {"modgetorset external:skip"}} {
    # Load the module
    test {Load modgetorset module} {
        r module load $testmodule
    } {OK}

    test {MOD_GET_OR_SET sets value when key does not exist} {
        # Delete the key to ensure it doesn't exist
        r del testkey1
        set result [r MOD_GET_OR_SET testkey1 0]
        assert_equal $result "0"
        # Verify the value was actually set
        assert_equal [r get testkey1] "0"
    }

    test {MOD_GET_OR_SET returns existing value without overwriting} {
        # Set a value first
        r set testkey2 42
        set result [r MOD_GET_OR_SET testkey2 100]
        assert_equal $result "42"
        # Verify the original value was not overwritten
        assert_equal [r get testkey2] "42"
    }

    test {MOD_GET_OR_SET returns existing value for different default value} {
        # Set a value
        r set testkey3 "hello"
        set result [r MOD_GET_OR_SET testkey3 "world"]
        assert_equal $result "hello"
        # Verify unchanged
        assert_equal [r get testkey3] "hello"
    }

    test {MOD_GET_OR_SET handles string values} {
        r del testkey4
        set result [r MOD_GET_OR_SET testkey4 "test_value"]
        assert_equal $result "test_value"
        assert_equal [r get testkey4] "test_value"
    }

    test {MOD_GET_OR_SET handles numeric values} {
        r del testkey5
        set result [r MOD_GET_OR_SET testkey5 12345]
        assert_equal $result "12345"
        assert_equal [r get testkey5] "12345"
    }

    test {MOD_GET_OR_SET overwrites existing value on key not exist} {
        # Set a value
        r set testkey6 "old_value"
        # Delete it
        r del testkey6
        # Now set a new value
        set result [r MOD_GET_OR_SET testkey6 "new_value"]
        assert_equal $result "new_value"
        assert_equal [r get testkey6] "new_value"
    }

    test {MOD_GET_OR_SET error on wrong number of arguments} {
        assert_error "*wrong number of arguments*" {r MOD_GET_OR_SET key}
        assert_error "*wrong number of arguments*" {r MOD_GET_OR_SET key val extra}
    }

    test {Unload the modgetorset module} {
        assert_equal {OK} [r module unload modgetorset]
    }
}
