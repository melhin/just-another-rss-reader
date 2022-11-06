import enum
import base64
from typing import Dict
from pathlib import Path
from tempfile import gettempdir

from pydantic import BaseSettings
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

    log_level: LogLevel = LogLevel.INFO

    # Variables for the database
    db_host: str = "localhost"
    db_port: int = 5432
    db_user: str = "reader"
    db_password: str = "reader"
    db_name: str = "reader"
    db_echo: bool = False
    ssl_enabled: bool = False
    ssl_cert_base64: str = ""
    auth_password: str = ""

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
            password=self.db_password,
            path=f"/{self.db_name}",
        )

    @property
    def ssl_params(self) -> Dict:
        # Encode like this
        # with open("cert.crt") as fh: base64.b64encode(fh.read().encode('ascii'))
        file_path = "/tmp/ca_file_path.crt"
        if self.ssl_enabled and self.ssl_cert_base64:
            base64_bytes = self.ssl_cert_base64.encode("ascii")
            message_bytes = base64.b64decode(base64_bytes)
            with open(file_path, "wb") as fh:
                fh.write(message_bytes)
            return {"sslmode": "require", "sslrootcert": file_path}
        return {}

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
