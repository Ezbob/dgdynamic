import typing as tp
import mod


Real = tp.Union[float, int]
Reals = tp.List[Real]
Numbers = tp.Union[Reals, Real]
Countable_Sequence = tp.Union[tp.List[tp.Any], tp.Tuple[tp.Any, ...], tp.Set[tp.Any]]
ODE_Function = tp.Callable[[Numbers, Numbers], Numbers]
MødHyperEdge = mod.DGHyperEdge
MødHyperVertex = mod.DGVertex
MødDeviationGraph = mod.DG
