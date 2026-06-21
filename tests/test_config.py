from dataclasses import replace

import pytest

from backend.core.config import settings


def test_production_settings_require_secure_https_configuration():
    insecure = replace(
        settings,
        app_env="production",
        secret_key="x" * 48,
        secure_cookies=False,
        allowed_origins=("http://example.com",),
        frontend_url="http://example.com",
    )

    with pytest.raises(RuntimeError, match="SECURE_COOKIES"):
        insecure.validate()


def test_production_settings_accept_explicit_https_configuration():
    production = replace(
        settings,
        app_env="production",
        secret_key="x" * 48,
        secure_cookies=True,
        allowed_origins=("https://example.com",),
        frontend_url="https://example.com",
    )

    production.validate()
