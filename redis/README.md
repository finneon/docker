# Find all domain which use Mask URL

### Start a new container running Redis
**Start redis container**
```
docker run -d -p 6379:6379 --name redis1 redis
docker exec -it redis1 sh
127.0.0.1:6379> ping
PONG
127.0.0.1:6379> set name mark
OK
127.0.0.1:6379> get name
"mark"
127.0.0.1:6379> incr counter
(integer) 1
127.0.0.1:6379> incr counter
(integer) 2
127.0.0.1:6379> get counter
"2"

**Connect from another linked container**
docker run -it --rm --link redis1:redis --name client1 redis bash
# redis-cli -h redis
redis:6379>
redis:6379> get name
"mark"
redis:6379> get counter
"2"

### Python client for Redis key-value store
```
pip install redis --user
```
