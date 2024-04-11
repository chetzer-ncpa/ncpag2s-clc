from configparser import ConfigParser
import os

default_config_file = os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    'default.config')

def default_config(parser=None,file=default_config_file):
    if not parser:
        parser = ConfigParser(strict=False)
    with open(file,'rt') as fid:
        parser.read_file(fid)
    return parser
