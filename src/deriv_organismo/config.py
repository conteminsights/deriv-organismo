from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_env: str = "dev"
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    database_url: str
    redis_url: str
    deriv_app_id: str = ""
    deriv_api_base_ws: str = "wss://ws.derivws.com/websockets/v3"
    deriv_api_base_rest: str = "https://api.deriv.com"
    default_account_slug: str = "primary"
    enable_multi_tenant: bool = False
