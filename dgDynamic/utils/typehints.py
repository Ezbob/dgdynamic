import typing as tp
import enum
import mod


Real = tp.Union[float, int]
Reals = tp.List[Real]
Numbers = tp.Union[Reals, Real]
Countable_Sequence = tp.Union[list, tuple, set]
Input_Type = tp.Union[Countable_Sequence, dict]
Opt_Input_Type = tp.Optional[Input_Type]
ODE_Function = tp.Callable[[Numbers, Numbers], Numbers]
MødHyperEdge = mod.DGHyperEdge
MødHyperVertex = mod.DGVertex
MødDeviationGraph = mod.DG
Enum = enum.Enum

