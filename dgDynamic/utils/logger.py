import logging
import os
import dgDynamic.config as config
import shutil

logging_handler = None


def set_logging():
    """
    This function setups the root logging system for use with the logging mixin.
    All log statements gets written to a log file
    :param filename: the name of the log file
    :param new_session: whether to delete all previous log files in the log directory
    :param level: maximum log level to log for
    """
    global logging_handler
    if logging_handler is None:
        log_dir_name = config.LOG_DIRECTORY if config.LOG_DIRECTORY else "logs"
        filename = config.SYSTEM_LOG_FILE if config.SYSTEM_LOG_FILE else "system.log"
        level = config.LOG_LEVEL if isinstance(config.LOG_LEVEL, type(logging.INFO)) else logging.INFO
        new_session = not config.SAVE_LOGS if isinstance(config.SAVE_LOGS, bool) else False

        log_dir = os.path.abspath(log_dir_name)
        make_directory(log_dir, pre_delete=new_session)

        new_file_path = os.path.join(log_dir, filename)

        logging_handler = logging.FileHandler(new_file_path)
        logging_handler.setFormatter(logging.Formatter('%(asctime)s %(name)s %(levelname)s %(message)s'))
        logging.basicConfig(level=level)


def make_directory(path, pre_delete=False):
    """
    This function just provides a mkdir functionality that can delete the contents of a
    folder if so needed.
    :param path: path the new directory
    :param pre_delete: shall it destroy the already existing folder?
    :return: None
    """
    if os.path.exists(path) and pre_delete is True:
            shutil.rmtree(path)
            os.mkdir(path)
    elif not os.path.exists(path):
        os.mkdir(path)

set_logging()
