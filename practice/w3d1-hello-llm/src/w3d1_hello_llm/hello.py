import httpx
from w3d1_hello_llm.settings import Settings



def main():
    s = Settings()
    r = httpx.post(
        f"{s.base_url}/chat/completions",
        headers={"Authorization": f"Bearer {s.api_key}"},
        json={
            "model": s.model,
            "messages": [
                {"role": "system", "content": "你是一位简洁的编程老师,回答不超过三行。"},
                {"role": "user", "content": "什么是 API?"},
            ],
            "max_tokens": 5,
        },
        timeout=60,  # 生成要几秒~几十秒,httpx 默认 5 秒会超时
    )
    try:
        r.raise_for_status()
    except httpx.HTTPStatusError  as e:
        if e.response and e.response.status_code == 401:
            print("401:API Key 无效,检查 .env")
        else:
            print(f"HTTPStatusError: {e}")
        return
    data = r.json()
    print(data["choices"][0]["message"]["content"])
    print("usage:", data["usage"])  # prompt_tokens / completion_tokens / total_tokens

if __name__ == "__main__":
    main()