from dgDynamic.simulators.ode_simulator import ODESystem
from dgDynamic.simulators.stochastic_pi_simulator import StochasticPiSystem
from typing import Union
from dgDynamic.utils.project_utils import LogMixin
import enum


def dgDynamicSim(graph, simulator_choice="ode", unchanging_species=()) -> Union[ODESystem, StochasticPiSystem]:

    if isinstance(simulator_choice, str):
        if simulator_choice.strip().lower() == "ode":
            return ODESystem(graph=HyperGraph(graph)).unchanging_species(*unchanging_species)
        elif simulator_choice.strip().lower() == "stochastic":
            return StochasticPiSystem(graph=HyperGraph(graph)).unchanging_species(*unchanging_species)
    elif isinstance(simulator_choice, enum.Enum):
        if simulator_choice.name.lower() == "ode":
            return ODESystem(graph=HyperGraph(graph)).unchanging_species(*unchanging_species)
        elif simulator_choice.name.lower() == "stochastic_pi":
            return StochasticPiSystem(graph=HyperGraph(graph)).unchanging_species(*unchanging_species)
    else:
        return None


class HyperGraph(LogMixin):
    def __init__(self, graph):
        if isinstance(graph, (tuple, list, set)):
            self.vertices, self.edges = graph[0], graph[1]
        elif isinstance(graph, dict):
            self.vertices, self.edges = graph['vertices'], graph['edges']
        elif hasattr(graph, "vertices") and hasattr(graph, "edges"):
            self.vertices, self.edges = graph.vertices, graph.edges
        else:
            raise TypeError('Object "{}" does not have any vertices or edges'.format(graph))
        self.edge_finder = graph.findEdge if hasattr(graph, "findEdge") else None

    def find_edge(self, vertices, edges):
        if self.edge_finder is not None:
            return self.edge_finder(vertices, edges)


class HyperEdge:
    def __init__(self, educts, products, is_one_way=True):
        self.educts = tuple(educts) if not isinstance(educts, (tuple, list, set)) else educts
        self.products = tuple(products) if not isinstance(products, (tuple, list, set)) else products
        self.is_one_way = is_one_way

    def __str__(self):
        if self.is_one_way:
            return "{} -> {}".format(" + ".join(self.educts), " + ".join(self.products))
        else:
            return "{} <=> {}".format(" + ".join(self.educts), " + ".join(self.products))

    def __repr__(self):
        return self.__str__()

