import enum

ODE_MODULE_PRECISION = "double"
PLOT_DIRECTORY = "plots"


class SupportedSolvers(enum.Enum):
    Scipy = "scipy"
    Matlab = "matlab"