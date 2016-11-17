import os.path
import sys

# Setting the Python Path so we can use dgDynamic
dynamic_module_path = os.path.abspath("../../")
sys.path.append(dynamic_module_path)

from dgDynamic import dgDynamicSim, show_simulation_plots
from dgDynamic.structures import AbstractReaction, HyperEdge, HyperGraph


include("grammar.py")

predicateRight = lambda d: all(a.vLabelCount("C") <= 5 for a in d.right)

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

flow_graph = HyperGraph.from_flow_solution(solution)

ode = dgDynamicSim(flow_graph)
stochastic = dgDynamicSim(flow_graph, simulator_choice="stochastic")

parameters = {AbstractReaction(dg, edge): 0.5 for edge in ode.abstract_edges}

initial_conditions = {
    'Formaldehyde': 20,
    'Glycolaldehyde': 20,
}

sim_range = (0, 15)

scipy = ode("scipy")

scipy(sim_range, initial_conditions, parameters).plot(filename="scipy_plot.png",
    figure_size=(40, 20), title="Formose cycle solution simulation")

#sim_range = (100, 100)

# Not working due to how the naming convention of generic compounds are in MØD (P_{0,0} and so on).
# Pretty sure it is the either the curly brackets or the in-name underscore
#for i in range(3):
#    stochastic("spim")(sim_range, initial_conditions, parameters, timeout=120).plot(
#        filename="spim_plot{}.png".format(i), figure_size=(40, 20), title="{}. Formose cycle solution simulation")

show_simulation_plots()

#def get_flow_solution_graph(solution):
#    """Get a tuple of hyper vertices and hyper edges from a flow solution"""
#    orign_graph = solution.dgFlow.dg
#    return tuple( v for v in orign_graph.vertices if solution.eval(vertex(v.graph)) != 0.0),
# tuple( e for e in orign_graph.edges if solution.eval(edge(e)) != 0.0)

