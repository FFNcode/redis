# modgetorset - Redis Module for MOD_GET_OR_SET command

CC = cc
CFLAGS = -O2 -Wall -Wextra -g -std=c11
RM_INCLUDE = ../../src

modgetorset.so: modgetorset.c
	$(CC) $(CFLAGS) -I$(RM_INCLUDE) -fPIC -shared -o $@ $<

clean:
	rm -f modgetorset.so
