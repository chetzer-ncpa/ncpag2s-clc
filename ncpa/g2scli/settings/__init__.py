from configparser import ConfigParser
from ncpa.g2scli.settings.default import default_config
from ncpa.g2scli.settings.user import user_config

config = user_config(parser=default_config())
