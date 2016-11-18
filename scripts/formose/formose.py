import os.path
import sys

# Setting the Python Path so we can use dgDynamic
dynamic_module_path = os.path.abspath("../../")
sys.path.append(dynamic_module_path)

from dgDynamic import dgDynamicSim, show_simulation_plots
from dgDynamic.structures import HyperGraph


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

sim_range = (0, 200)

scipy = ode("scipy")

scipy(sim_range, initial_conditions, parameters).plot(filename="scipy_plot.png",
    figure_size=(40, 20), title="SciPy VODE Formose cycle solution simulation")

sim_range = (200, 2000)

for i in range(10):
    stochastic("spim")(sim_range, initial_conditions, parameters, timeout=120).plot(
        filename="spim_plot{}.png".format(i), figure_size=(40, 20), title="SPIM {}. Formose cycle solution simulation".format(i + 1))

show_simulation_plots()

#def get_flow_solution_graph(solution):
#    """Get a tuple of hyper vertices and hyper edges from a flow solution"""
#    orign_graph = solution.dgFlow.dg
#    return tuple( v for v in orign_graph.vertices if solution.eval(vertex(v.graph)) != 0.0),
# tuple( e for e in orign_graph.edges if solution.eval(edge(e)) != 0.0)

