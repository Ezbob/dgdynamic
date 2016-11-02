import logging
import os
import dgDynamic.utils.config as project_config
import shutil

logging_handler = None


def set_logging(config_file="default_config.ini"):
    """
    This function setups the root logging system for use with the logging mixin.
    All log statements gets written to a log file
    :param config_file:
    :param filename: the name of the log file
    :param new_session: whether to delete all previous log files in the log directory
    :param level: maximum log level to log for
    """
    global logging_handler
    if logging_handler is None:
        project_config.set_config(filename=config_file)
        log_config = project_config.config['Logging']

        log_dir_name = project_config.config['Output Paths']['LOG_DIRECTORY']
        filename = log_config['SYSTEM_LOG_FILE']

        level = logging.getLevelName(log_config['LOG_LEVEL']) \
            if isinstance(logging.getLevelName(log_config['LOG_LEVEL']), int) else logging.INFO
        new_session = not bool(log_config['SAVE_LOGS'])

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
