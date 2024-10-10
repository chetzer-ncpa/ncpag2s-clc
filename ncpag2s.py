#!/usr/bin/env python
"""Command-line utility to interface with the G2S system."""
import sys
import os

MIN_PYTHON_VERSION = (3,9)
if sys.version_info < MIN_PYTHON_VERSION:
    sys.exit("Python %s.%s or later is required.\n" % MIN_PYTHON_VERSION)

def main():
    """Run administrative tasks."""
    try:
        from ncpa.g2scli import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import ncpacli libraries. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    scriptpath = os.path.dirname(os.path.realpath(__file__))
    if scriptpath not in sys.path:
        sys.path.insert(0,scriptpath)
    main()
