import configparser
import os.path

config = configparser.ConfigParser()
config.read_file(open(os.path.join(os.path.dirname(__file__), 'default_config.ini')))
config.read(os.path.join(os.path.abspath(os.path.curdir), 'config.ini'))
