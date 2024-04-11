import sys
import os
from pathlib import Path


from ncpa.g2scli.settings import config
from ncpa.g2scli.commands import ModularCommand
from ncpa.g2scli.version import get_version

from configparser import ConfigParser

VERSION = (0, 1, 0, "beta", 0)
APPS = ('g2scli')

def g2scli_base_dir():
    base = Path(os.path.realpath(__file__))
    base.resolve()
    return base.parent.parent.parent

def execute_from_command_line(argv=None):
    """Run a ModularCommand."""
    utility = ModularCommand(argv)
    utility.execute()

