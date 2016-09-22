import enum

ODE_MODULE_PRECISION = "double"
DATA_DIRECTORY = "data"
LOG_DIRECTORY = "logs"


class SupportedSolvers(enum.Enum):
    Scipy = "scipy"
    Matlab = "matlab"