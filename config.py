import enum

ODE_MODULE_PRECISION = "double"
PLOT_DIRECTORY = "plots"
LOG_DIRECTORY = "logs"

class SupportedSolvers(enum.Enum):
    Scipy = "scipy"
    Matlab = "matlab"