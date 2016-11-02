import configparser
import os.path

config = None

if os.path.isfile(os.path.join(os.path.abspath(os.path.curdir), 'config.ini')):
    config = configparser.ConfigParser()
    config.read(os.path.join(os.path.abspath(os.path.curdir), 'config.ini'))
else:
    config = configparser.ConfigParser()
    config.read(os.path.join(os.path.abspath("dgDynamic"), 'default_config.ini'))
