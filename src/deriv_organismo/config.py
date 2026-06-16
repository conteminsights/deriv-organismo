from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


DEFAULT_DEV_DATABASE_URL = 'sqlite+aiosqlite:///./deriv-organismo.db'
DEFAULT_REDIS_URL = 'redis://localhost:6379/0'
DEFAULT_APP_SECRET_KEY = 'dev-app-secret-key-change-in-production'
DEFAULT_CREDENTIAL_SECRET_KEY = 'dev-credential-secret-key-change-in-production'


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')

    app_env: str = 'dev'
    app_host: str = '0.0.0.0'
    app_port: int = 8000
    database_url: str | None = None
    redis_url: str = DEFAULT_REDIS_URL
    app_secret_key: str = DEFAULT_APP_SECRET_KEY
    credential_secret_key: str = DEFAULT_CREDENTIAL_SECRET_KEY
    auth_enabled: bool = False
    master_email: str | None = None
    master_password: str | None = None
    tenant_email: str | None = None
    tenant_password: str | None = None
    tenant_scope_id: str | None = None
    deriv_app_id: str = ''
    deriv_api_base_ws: str = 'wss://ws.derivws.com/websockets/v3'
    deriv_api_base_rest: str = 'https://api.deriv.com'
    default_account_slug: str = 'primary'
    enable_multi_tenant: bool = False

    @model_validator(mode='after')
    def apply_defaults_and_guards(self) -> 'Settings':
        env = self.app_env.lower()

        if not self.database_url:
            if env in {'dev', 'local', 'test'}:
                self.database_url = DEFAULT_DEV_DATABASE_URL
            else:
                raise ValueError('DATABASE_URL is required for non-dev environments')

        if self.auth_enabled and not (
            self.master_email
            and self.master_password
            and self.tenant_email
            and self.tenant_password
            and self.tenant_scope_id
        ):
            raise ValueError('auth_enabled requires master and tenant credentials in settings')

        if env not in {'dev', 'local', 'test'}:
            if self.app_secret_key == DEFAULT_APP_SECRET_KEY:
                raise ValueError('APP_SECRET_KEY is required outside dev/local/test')
            if self.credential_secret_key == DEFAULT_CREDENTIAL_SECRET_KEY:
                raise ValueError('CREDENTIAL_SECRET_KEY is required outside dev/local/test')

        return self
