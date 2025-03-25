#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""

import os
import sys


def load_local_env():
    from dotenv import load_dotenv

    from core.paths import PROJECT_DIR

    load_dotenv(
        dotenv_path=PROJECT_DIR / ".envs/.env.local",
    )


def main():
    """Run administrative tasks."""
    os.environ.get("DJANGO_SETTINGS_MODULE", "core.settings.dev")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    DJANGO_LOCAL = os.environ.get("DJANGO_LOCAL", "1") == "1"
    if DJANGO_LOCAL:
        load_local_env()
    main()
