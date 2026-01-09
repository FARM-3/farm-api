#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
# ONLY for development on http://localhost or http://127.0.0.1
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

import os
import sys


def main():
    """Run administrative tasks."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "api.settings")
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
    main()
