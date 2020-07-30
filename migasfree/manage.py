#!/usr/bin/python3
import os
import sys

if __name__ == "__main__":
    sys.path.append('.')
    os.environ.setdefault(
        "DJANGO_SETTINGS_MODULE", "migasfree.settings.production"
    )

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
