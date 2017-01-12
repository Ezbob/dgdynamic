import configparser
import os.path

config = None

default_config_file = 'default_config.ini'

config_file_names = [
    'config.ini',
]

if __name__ == "__main__":
    from sys import stderr
    print("Configuration loader not meant as standalone script", file=stderr)
else:
    config = configparser.ConfigParser()
    config.read_file(open(os.path.join(os.path.dirname(__file__), default_config_file)))
    config_file_loaded = config.read([os.path.join(os.path.abspath(os.path.curdir), name)
                                      for name in config_file_names])


def logging_is_enabled():
    if config is None:
        return False
    return config.getboolean('Logging', 'ENABLE_LOGGING', fallback=False)
