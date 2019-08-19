#!/usr/bin/env python
""" Sample code of searching domain with mask url """

import redis

r = redis.Redis(host='localhost', port=6379, db=0)
r.set("foo", "bar")
r.get("foo")

for key in r.scan_iter(match="pattern"):
    data = r.hgetall(key)
