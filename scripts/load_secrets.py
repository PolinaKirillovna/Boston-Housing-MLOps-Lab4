"""Render a transient .env for docker-compose from the Ansible Vault secrets.

docker-compose needs the MS SQL password at parse time to configure the
database container (MSSQL_SA_PASSWORD) and the one-shot mssql-init job. Those
values are decrypted from secrets/secrets.yml here and written to a local
.env file, which is git-ignored and is meant to be deleted right after the
stack run:

    python scripts/load_secrets.py
    docker compose up -d
    ...
    docker compose down -v
    rm -f .env

The api service itself does NOT depend on this file: it decrypts the vault
in-process at startup (see bootstrap_secrets.load_secrets_into_env), which is
how the model service obtains its database credentials.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from bootstrap_secrets import load_secrets  # noqa: E402

ENV_PATH = ROOT / ".env"

# Non-secret values docker-compose needs for variable substitution.
STATIC = {"MSSQL_USER": "sa"}


def main() -> None:
    secrets = load_secrets()
    mssql_password = secrets.get("MSSQL_PASSWORD")
    if not mssql_password:
        raise SystemExit("MSSQL_PASSWORD is missing from the vault secrets.")

    lines = [f"{key}={value}" for key, value in STATIC.items()]
    lines.append(f"MSSQL_PASSWORD={mssql_password}")

    kafka_cluster_id = secrets.get("KAFKA_CLUSTER_ID")
    if kafka_cluster_id:
        lines.append(f"KAFKA_CLUSTER_ID={kafka_cluster_id}")

    ENV_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {ENV_PATH} for docker-compose (delete it after the run).")


if __name__ == "__main__":
    main()
