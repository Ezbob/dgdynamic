from dgDynamic.choices import SupportedStochasticPlugins, SupportedOdePlugins
import dgDynamic.plugins.stochastic.stochpy.stochpy as stochpy
import dgDynamic.plugins.stochastic.spim.spim as spim
import dgDynamic.plugins.ode.scipy.scipy as scipy
import dgDynamic.plugins.ode.matlab.matlab as matlab

PLUGINS_TAB = {
    'stochastic': {
        SupportedStochasticPlugins.StochPy: stochpy.StochPyStochastic,
        SupportedStochasticPlugins.SPiM: spim.SpimStochastic
    },
    'ode': {
        SupportedOdePlugins.SciPy: scipy.ScipyOde,
        SupportedOdePlugins.MATLAB: matlab.MatlabOde
    }
}
