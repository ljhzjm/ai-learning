import asyncio, time

async def fetch(i: int):           # async def 声明协程
    await asyncio.sleep(1)         # 模拟:等网络 1 秒,await = 让出执行权
    return f"结果 {i}"

# 写法 A:串行 —— 一个一个等
async def serial():
    t0 = time.perf_counter()
    results = []
    for i in range(10):
        r = await fetch(i)         # 必须等完 1 秒才轮到下一个
        results.append(r)
    return results, time.perf_counter() - t0

# 写法 B:并发 —— 一起等
async def parallel():
    try:
        t0 = time.perf_counter()
        results = await asyncio.wait_for(
            asyncio.gather(*[fetch(i) for i in range(10)]), timeout=10)
    except asyncio.TimeoutError:
        print("TimeoutError")
    return results, time.perf_counter() - t0

async def main():
    r1, t1 = await serial()
    r2, t2 = await parallel()
    print(f"串行 10 个:{t1:.2f}s  并发 10 个:{t2:.2f}s  提速 {t1/t2:.0f} 倍")

asyncio.run(main())   # ← 事件循环的启动入口,永远在脚本最底部