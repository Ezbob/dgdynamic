from .simulator import DynamicSimulator
from typing import Union
from dgDynamic.utils.project_utils import ProjectTypeHints


class StochasticPiSystem(DynamicSimulator):

    def __init__(self, graph):
        super().__init__(graph=graph)
        self.reaction_names = tuple('r{}'.format(index) for index in range(self.reaction_count))
        print(self.reaction_names)

    def unchanging_species(self, *species: Union[str, "Symbol", ProjectTypeHints.Countable_Sequence]):
        pass
