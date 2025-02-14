import enum
from pathlib import Path
from tempfile import gettempdir

from pydantic_settings import BaseSettings, SettingsConfigDict
from yarl import URL

TEMP_DIR = Path(gettempdir())


class LogLevel(str, enum.Enum):  # noqa: WPS600
    """Possible log levels."""

    NOTSET = "NOTSET"
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    FATAL = "FATAL"


class Settings(BaseSettings):
    """
    Application settings.

    These parameters can be configured
    with environment variables.
    """

    host: str = "127.0.0.1"
    port: int = 8000
    # quantity of workers for uvicorn
    workers_count: int = 1
    # Enable uvicorn reloading
    reload: bool = False

    # static file directory
    static_dir: str = "./app/static"

    # Current environment
    environment: str = "dev"

    log_level: LogLevel = LogLevel.INFO

    # Variables for the database
    db_host: str = "localhost"
    db_port: int = 5432
    db_user: str = "dblab-emr"
    db_pass: str = "dblab-emr"
    db_base: str = "dblab-emr"
    db_echo: bool = False

    # Variables for Auth
    secret_key: str = "sample_secret_key"

    # Variables for minio
    minio_host: str = "localhost"
    minio_port: int = 9000
    minio_access_key: str = ""
    minio_secret_key: str = ""
    minio_default_bucket: str = "files"

    # Variables for OCR
    ocr_secret: str = ""

    @property
    def db_url(self) -> URL:
        """
        Assemble database URL from settings.

        :return: database URL.
        """
        return URL.build(
            scheme="postgresql+asyncpg",
            host=self.db_host,
            port=self.db_port,
            user=self.db_user,
            password=self.db_pass,
            path=f"/{self.db_base}",
        )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="DBLAB_EMR_",
        env_file_encoding="utf-8",
    )


settings = Settings()
