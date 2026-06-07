"""Load application secrets from an Ansible Vault encrypted file.

The model service does not keep database credentials or the JWT secret in a
plaintext file committed to the repository. Instead they live in an
ansible-vault encrypted file (``secrets/secrets.yml``), and the service
decrypts them at startup. The vault password is supplied either via the
``ANSIBLE_VAULT_PASSWORD`` environment variable (used in CI/CD) or a local
``secrets/.vault_pass`` file that is kept out of version control.

If neither a password nor the encrypted file is available (for example during
unit tests) loading is silently skipped, so callers can fall back to
environment variables provided by the test harness.
"""

from __future__ import annotations

import os
from pathlib import Path

import yaml

BASE_DIR = Path(__file__).resolve().parent
SECRETS_FILE = BASE_DIR / "secrets" / "secrets.yml"
VAULT_PASS_FILE = BASE_DIR / "secrets" / ".vault_pass"


def get_vault_password() -> str | None:
    """Return the vault password from the environment or the local file."""
    password = os.getenv("ANSIBLE_VAULT_PASSWORD")
    if password:
        return password.strip()
    if VAULT_PASS_FILE.exists():
        return VAULT_PASS_FILE.read_text(encoding="utf-8").strip()
    return None


def load_secrets(secrets_file: Path = SECRETS_FILE) -> dict:
    """Decrypt the vault file and return the secrets as a dictionary.

    Raises:
        FileNotFoundError: If the encrypted secrets file does not exist.
        RuntimeError: If the vault password is not available.
        ValueError: If the decrypted payload is not a YAML mapping.
    """
    if not secrets_file.exists():
        raise FileNotFoundError(f"Encrypted secrets file not found: {secrets_file}")

    password = get_vault_password()
    if not password:
        raise RuntimeError(
            "Vault password is not set. Provide ANSIBLE_VAULT_PASSWORD or "
            "create secrets/.vault_pass."
        )

    # Imported lazily so that environments without ansible (none expected in
    # production, but cheap insurance) only pay the cost when decrypting.
    from ansible.parsing.vault import VaultLib, VaultSecret

    vault = VaultLib([("default", VaultSecret(password.encode("utf-8")))])
    decrypted = vault.decrypt(secrets_file.read_bytes())

    data = yaml.safe_load(decrypted) or {}
    if not isinstance(data, dict):
        raise ValueError("Vault secrets file must contain a YAML mapping.")
    return data


def load_secrets_into_env(*, override: bool = False) -> bool:
    """Inject decrypted secrets into ``os.environ``.

    Existing variables are preserved unless ``override`` is True, so test and
    CI environments can supply their own values.

    Returns:
        True if secrets were loaded, False if loading was skipped (no
        encrypted file or no vault password available).
    """
    if not SECRETS_FILE.exists() or not get_vault_password():
        return False

    for key, value in load_secrets().items():
        if override or key not in os.environ:
            os.environ[str(key)] = str(value)
    return True
