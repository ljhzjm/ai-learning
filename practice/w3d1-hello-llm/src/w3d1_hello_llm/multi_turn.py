import httpx
from w3d1_hello_llm.settings import Settings


def main():
  s = Settings()
  history = [{"role":"system","content":"你是一位简洁的助手,回答不超过两行。"}]
  print("输入quit退出.第一轮先告诉它你的名字")

  while True:
    text = input("你:").strip()
    if text.lower() == "quit":
      break
    history.append({"role":"user","content":text})
    r = httpx.post(
       f"{s.base_url}/chat/completions",
            headers={"Authorization": f"Bearer {s.api_key}"},
            json={"model": s.model, "messages": history, "max_tokens": 200},
            timeout=60,
    )
    r.raise_for_status()
    answer = r.json()["choices"][0]["message"]["content"]
    print("AI:", answer)
    history.append({"role": "assistant", "content": answer})  # ← 记忆的关键一行

if __name__ == "__main__":
    main()
