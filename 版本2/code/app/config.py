from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "故事与星空慢游规划 API"
    # 可通过环境变量 SQLITE_PATH 覆盖；测试可使用 SQLITE_PATH=:memory:
    sqlite_path: str = "./slowtravel.db"
    # 写操作（POST/PATCH/DELETE）需 Header: X-API-Key。设为空字符串则关闭校验（仅本地调试建议）。
    api_key: str = Field(default="dev-api-key", description="API key for write operations")


settings = Settings()
