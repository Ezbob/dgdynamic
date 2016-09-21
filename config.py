import enum

ODE_MODULE_PRECISION = "double"


class SupportedSolvers(enum.Enum):
    Scipy = "scipy"
    Matlab = "matlab"