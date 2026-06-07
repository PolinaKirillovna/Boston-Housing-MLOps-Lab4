"""Application package.

Decrypt Ansible Vault secrets into the environment as early as possible, so
every submodule (database session, auth) sees the credentials when imported.
"""

from bootstrap_secrets import load_secrets_into_env

load_secrets_into_env()
