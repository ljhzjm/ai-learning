from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "待办事项 API"
    debug: bool = False                 # debug=true 时打印每条 SQL(echo)
    database_url: str = ""
    model_config = {"env_file": ".env", "env_prefix": "TODO_", "extra": "ignore"}

settings = Settings()