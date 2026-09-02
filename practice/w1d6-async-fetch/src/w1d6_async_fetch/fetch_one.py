import asyncio, httpx

async def main():
    async with httpx.AsyncClient(timeout=10) as client:  # 每个请求最多 10 秒
        r = await client.get("https://api.github.com/zen")  # GitHub 名言接口
        print(r.status_code)
        print(r.text[:100])

asyncio.run(main())