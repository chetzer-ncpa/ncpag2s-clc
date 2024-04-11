import sys
import os


from ncpa.g2scli.settings import config
from ncpa.g2scli.commands import ModularCommand
from ncpa.g2scli.version import get_version

from configparser import ConfigParser

VERSION = (0, 2, 0, "beta", 0)
APPS = ('g2scli')


def execute_from_command_line(argv=None):
    """Run a ModularCommand."""
    utility = ModularCommand(argv)
    utility.execute()

