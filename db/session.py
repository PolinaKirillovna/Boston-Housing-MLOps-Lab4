import os
from urllib.parse import quote_plus

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from bootstrap_secrets import load_secrets_into_env

# Obtain database credentials by decrypting the Ansible Vault file (if present).
load_secrets_into_env()


def _get_required_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Required environment variable '{name}' is not set.")
    return value


def build_connection_url() -> str:
    server = _get_required_env("MSSQL_SERVER")
    port = _get_required_env("MSSQL_PORT")
    database = _get_required_env("MSSQL_DATABASE")
    username = _get_required_env("MSSQL_USER")
    password = _get_required_env("MSSQL_PASSWORD")
    driver = os.getenv("MSSQL_DRIVER", "ODBC Driver 18 for SQL Server")

    return (
        f"mssql+pyodbc://{username}:{quote_plus(password)}@{server}:{port}/{database}"
        f"?driver={quote_plus(driver)}"
        f"&Encrypt=no"
        f"&TrustServerCertificate=yes"
    )


DATABASE_URL = build_connection_url()

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    future=True,
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    future=True,
)
