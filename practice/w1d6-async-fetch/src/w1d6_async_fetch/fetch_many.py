import asyncio, time, httpx

URLS = [
    "https://api.github.com/repos/fastapi/fastapi",
    "https://api.github.com/repos/encode/httpx",
    "https://api.github.com/repos/psf/requests",
    "https://api.github.com/repos/astral-sh/uv",
    "https://api.github.com/repos/pydantic/pydantic",
    "https://api.github.com/repos/python/cpython",
    "https://api.github.com/repos/microsoft/vscode",
    "https://api.github.com/repos/nodejs/node",
    "https://api.github.com/repos/docker/compose",
    "https://api.github.com/repos/redis/redis",
]

async def fetch(client: httpx.AsyncClient, url: str):
    t0 = time.perf_counter()
    r = await client.get(url)
    dt = (time.perf_counter() - t0) * 1000
    return f"{r.status_code}  {dt:6.0f}ms  {url}"

async def serial(client):
    t0 = time.perf_counter()
    for url in URLS:
        print(await fetch(client, url))
    return time.perf_counter() - t0

async def parallel(client):
    t0 = time.perf_counter()
    lines = await asyncio.gather(*[fetch(client, u) for u in URLS])
    for line in lines:
        print(line)
    return time.perf_counter() - t0

async def main():
    async with httpx.AsyncClient(timeout=10) as client:
        t_s = await serial(client)
        print(f"\n串行总耗时:{t_s:.2f}s\n" + "=" * 50)
        t_p = await parallel(client)
        print(f"\n并发总耗时:{t_p:.2f}s  提速 {t_s/t_p:.1f} 倍")

asyncio.run(main())