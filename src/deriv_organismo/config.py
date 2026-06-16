from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


DEFAULT_DEV_DATABASE_URL = 'sqlite+aiosqlite:///./deriv-organismo.db'
DEFAULT_REDIS_URL = 'redis://localhost:6379/0'


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')

    app_env: str = 'dev'
    app_host: str = '0.0.0.0'
    app_port: int = 8000
    database_url: str | None = None
    redis_url: str = DEFAULT_REDIS_URL
    deriv_app_id: str = ''
    deriv_api_base_ws: str = 'wss://ws.derivws.com/websockets/v3'
    deriv_api_base_rest: str = 'https://api.deriv.com'
    default_account_slug: str = 'primary'
    enable_multi_tenant: bool = False

    @model_validator(mode='after')
    def apply_database_defaults(self) -> 'Settings':
        if self.database_url:
            return self
        if self.app_env.lower() in {'dev', 'local', 'test'}:
            self.database_url = DEFAULT_DEV_DATABASE_URL
            return self
        raise ValueError('DATABASE_URL is required for non-dev environments')
