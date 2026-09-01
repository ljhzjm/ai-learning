from w1d3_hello_uv.config import settings

def main() -> None:
    print(f"app_name     = {settings.app_name}")
    print(f"debug        = {settings.debug}")
    print(f"database_url = {settings.database_url}")