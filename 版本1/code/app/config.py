from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "故事与星空慢游规划 API"
    # 可通过环境变量 SQLITE_PATH 覆盖；测试可使用 SQLITE_PATH=:memory:
    sqlite_path: str = "./slowtravel.db"


settings = Settings()
