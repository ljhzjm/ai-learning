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

# 串行
async def serial(client):
  t0 = time.perf_counter()
  for url in URLS:
    try:
      r = await fetch(client, url)
      print(r)
    except Exception as e:
      print(f"{type(e).__name__}  {url}")
    return time.perf_counter() - t0

# 并发:return_exceptions=True 让单个失败变成"结果"而不是炸弹
async def parallel(client):
  t0 = time.perf_counter()
  try:
    lines = await asyncio.wait_for(
      asyncio.gather(*[fetch(client, u) for u in URLS], return_exceptions=True),
      timeout=10
    )
    for u, r in zip(URLS, lines):
      print(f"{type(r).__name__}  {u}" if isinstance(r, Exception) else r)
  except asyncio.TimeoutError:
    print("TimeoutError:整体超时,放弃剩余")
  return time.perf_counter() - t0

async def main():
  async with httpx.AsyncClient(timeout=10) as client:
    t_s = await serial(client)
    print(f"\n串行总耗时:{t_s:.2f}s\n" + "=" * 50)
    t_p = await parallel(client)
    print(f"\n并发总耗时:{t_p:.2f}s  提速 {t_s/t_p:.1f} 倍")

asyncio.run(main())