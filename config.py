import enum
import logging

# The maximal precision used in the different solvers (not used right now)
ODE_MODULE_PRECISION = "double"

# The name of the data directory for storing the integration data
DATA_DIRECTORY = "data"

# The name of the log directory where the log files are stored
LOG_DIRECTORY = "logs"

# Current logging level
LOG_LEVEL = logging.DEBUG

# If false, this removes the old logs when the application is restarted
SAVE_LOGS = True

# The name of the main log file
SYSTEM_LOG_FILE = "system.log"


class SupportedSolvers(enum.Enum):
    """
    Here we list the different solvers available in our system as key-value pairs.
    The value is the internal system name for the solver and is used when saving the data files etc.
    """
    Scipy = "scipy"
    Matlab = "matlab"