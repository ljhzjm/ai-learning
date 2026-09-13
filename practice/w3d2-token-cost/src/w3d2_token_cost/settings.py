from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="LLM_", extra="ignore")

    api_key: str
    base_url: str = "https://api.deepseek.com"
    model: str = "deepseek-chat"
    price_in_per_m: float = 2.0   # 元 / 百万 tokens,以官网价格页为准
    price_out_per_m: float = 8.0  # 元 / 百万 tokens,以官网价格页为准
