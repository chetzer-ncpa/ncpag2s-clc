from configparser import ConfigParser
import os


default_config = ConfigParser()
default_config_file = os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    'default.config')
default_config.read(default_config_file)