import enum


class SimulatorModes(enum.Enum):
    """
    This enum lists the available simulation modes
    """
    ODE = "ode"
    Stochastic_Pi = "stochastic"


class SupportedOdePlugins(enum.Enum):
    """
    Here we list the different solvers available in our system as key-value pairs.
    The value is the internal system name for the solver and is used when saving the data files etc.
    """
    Scipy = "scipy"
    Matlab = "matlab"


class SupportedStochasticPlugins(enum.Enum):
    SPiM = "spim"


class ScipyOdeSolvers(enum.Enum):
    """
    Enum representing different ode solver methods available to the Scipy solver
    """
    VODE = "vode"
    LSODA = "lsoda"
    DOPRI5 = "dopri5"
    DOP853 = "dop853"
    ZVODE = "zvode"


class MatlabOdeSolvers(enum.Enum):
    """
    Choose your MATLAB ode solver from this enum.
    """
    ode45 = "45"
    ode23 = "23"
    ode113 = "113"
    ode15s = "15s"
    ode23s = "23s"
    ode23t = "23t"
    ode23tb = "23tb"
    # ode15i = "15i" # for complex numbers
