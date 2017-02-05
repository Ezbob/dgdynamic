from dgDynamic.choices import SupportedStochasticPlugins, SupportedOdePlugins
import dgDynamic.plugins.stochastic.stochpy.stochpy as stochpy
import dgDynamic.plugins.stochastic.stochkit2.stochkit2 as stochkit2
import dgDynamic.plugins.stochastic.spim.spim as spim
import dgDynamic.plugins.ode.scipy.scipy as scipy
import dgDynamic.plugins.ode.matlab.matlab as matlab

PLUGINS_TAB = {
    'stochastic': {
        SupportedStochasticPlugins.StochPy: stochpy.StochPyStochastic,
        SupportedStochasticPlugins.StochKit2: stochkit2.StochKit2Stochastic,
        SupportedStochasticPlugins.SPiM: spim.SpimStochastic
    },
    'ode': {
        SupportedOdePlugins.SciPy: scipy.ScipyOde,
        SupportedOdePlugins.MATLAB: matlab.MatlabOde
    }
}
