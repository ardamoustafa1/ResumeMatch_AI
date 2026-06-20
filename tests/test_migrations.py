import pytest
from alembic.config import Config
from alembic import command
from pathlib import Path


def test_migrations_upgrade_downgrade():
    """
    Smoke test to verify that Alembic migrations can run upgrade head and downgrade base
    without crashing. We run this using the configured testing database.
    """
    alembic_ini_path = (
        Path(__file__).parent.parent / "backend" / "db" / "migrations" / "alembic.ini"
    )
    alembic_cfg = Config(str(alembic_ini_path))
    alembic_cfg.set_main_option(
        "script_location",
        str(Path(__file__).parent.parent / "backend" / "db" / "migrations"),
    )

    # Point alembic to the test DB
    import os
    alembic_cfg.set_main_option("sqlalchemy.url", os.environ["DATABASE_URL"])

    # Run upgrade head
    try:
        command.upgrade(alembic_cfg, "head")
    except Exception as e:
        pytest.fail(f"Alembic upgrade head failed: {e}")

    # Run downgrade base
    try:
        command.downgrade(alembic_cfg, "base")
    except Exception as e:
        pytest.fail(f"Alembic downgrade base failed: {e}")

    # Run upgrade head again to leave the DB in a usable state for other tests
    try:
        command.upgrade(alembic_cfg, "head")
    except Exception as e:
        pytest.fail(f"Alembic upgrade head (second pass) failed: {e}")
