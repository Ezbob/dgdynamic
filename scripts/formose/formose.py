from dgdynamic import dgDynamicSim, show_plots
from dgdynamic.structures import HyperGraph

include("grammar.py")


def predicateRight(d): return all(a.vLabelCount("C") <= 5 for a in d.right)

dg = dgRuleComp(inputGraphs,
    addSubset(inputGraphs)
    >> rightPredicate[predicateRight](
        repeat(inputRules)
    )
)

dg.calc()

flow = dgFlow(dg)
flow.overallAutocatalysis.enable()
flow.allowIOReverse = False

flow.addSource(formaldehyde)
flow.addSource(glycolaldehyde)
flow.addSink(glycolaldehyde)

flow.addConstraint(inFlow(formaldehyde) == 2)
flow.addConstraint(outFlow(glycolaldehyde) == 2)
flow.addConstraint(inFlow(glycolaldehyde) == 1)

flow.calc()

solution = list(flow.solutions)[0]

solution.print()

flow_graph = HyperGraph.from_flow_solution(solution)

ode = dgDynamicSim(flow_graph)
stochastic = dgDynamicSim(flow_graph, simulator_choice="stochastic")

parameters = {edge: 0.5 for edge in ode.abstract_edges}

initial_conditions = {
    'Formaldehyde': 100,
    'Glycolaldehyde': 1,
}

drain_parameters = {symbol: {
    'out': {
        'factor': 0.015
    }
} for symbol in ode.symbols}

drain_parameters['Formaldehyde'] = {'in': {
    'factor': 0.03
    }, 'out': {
    'factor': 0.015
    }
}

sim_range = (0, 300)

scipy = ode("scipy")

scipy_sol = scipy(sim_range, initial_conditions, parameters).plot(filename="closed_scipy_plot.png",
    figure_size=(40, 20), title="SciPy VODE Formose closed cycle solution simulation")

scipy(sim_range, initial_conditions, parameters, drain_parameters).plot(
    filename="open_scipy_plot.png",
    figure_size=(40, 20), title="SciPy VODE Formose open cycle solution simulation"
)

sim_range = (300, 2000)

for i in range(5):
    stochastic("spim")(sim_range, initial_conditions, parameters, timeout=120).plot(
        filename="spim_plot{}.png".format(i), figure_size=(40, 20),
        title="SPIM {}. Formose closed cycle solution simulation".format(i + 1))

for i in range(5):
    stochastic("spim")(sim_range, initial_conditions, parameters, drain_parameters, timeout=120).plot(
        filename="spim_plot{}.png".format(i), figure_size=(40, 20),
        title="SPIM {}. Formose open cycle solution simulation".format(i + 1))

with stochastic("stochkit2") as stochkit2:
    stochkit2.trajectories = 5
    stochkit2.method = "tauLeaping"
    output_set = stochkit2.simulate(sim_range, initial_conditions, parameters, drain_parameters, timeout=120 * 5)
    for index, output in enumerate(output_set):
        output.plot(filename="stochkit2_plot{}.png".format(index), figure_size=(40, 20),
                    title="StochKit2 {}. Formose open cycle solution simulation".format(index + 1))

show_plots()

