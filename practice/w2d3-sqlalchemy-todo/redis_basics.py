import redis, time

r = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)
# decode_responses=True:返回 str。不加这个,返回的是 bytes(b'xxx')——最经典的新手坑!

# ① 字符串:SET / GET / INCR(计数器)
r.set("greeting", "hello redis")
print(r.get("greeting"))                 # hello redis
r.incr("counter")                        # 不存在当 0 处理,变成 1
r.incr("counter")                        # 2
print(r.get("counter"))

# ② 哈希:HSET / HGETALL(存对象)
r.hset("todo:1", mapping={"title": "学 Redis", "done": "0", "priority": "2"})
print(r.hgetall("todo:1"))               # {'title': '学 Redis', 'done': '0', 'priority': '2'}
print(r.hget("todo:1", "title"))         # 学 Redis

# ③ 过期:EXPIRE / TTL
r.expire("greeting", 30)
print(r.ttl("greeting"))
time.sleep(1)
print(r.ttl("greeting"))