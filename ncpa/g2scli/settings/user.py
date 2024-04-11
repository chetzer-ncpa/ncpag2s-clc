from configparser import ConfigParser
import os
from pathlib import Path


THISDIR_ = Path(os.path.realpath(__file__))
THISDIR_.resolve()
BASEDIR_ = THISDIR_.parent.parent.parent.parent

def g2scli_base_dir():
    return BASEDIR_

user_config_file = os.path.join(
    g2scli_base_dir(),
    'user.config')

def user_config(parser=None,file=user_config_file):
    if not parser:
        parser = ConfigParser(strict=False)
    parser.read(file)
    return parser