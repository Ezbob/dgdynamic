from typing import Iterable, Tuple, Union


def _parse_sides(side: str):
    skip_next = False
    the_splitting = side.split()
    for index, atom in enumerate(the_splitting):
        if not skip_next:
            if str.isdigit(atom):
                skip_next = True
                multiplier = int(atom)
                try:
                    species = the_splitting[index + 1]
                except IndexError:
                    raise IndexError("Index error in\
                      specification parsing; tried index {} but length is {} ".format(index + 1,
                                                                                      len(the_splitting)))
                for i in range(multiplier):
                    yield species
            elif '+' == atom:
                continue
            yield atom
        else:
            skip_next = False
            continue


def _get_side_vertices(graph: object, side):
    for sym in _parse_sides(side):
        for vertex in graph.vertices:
            if vertex.graph.name == sym:
                yield vertex


def _break_two_way_deviations(two_way: str) -> Iterable[str]:
    yield " -> ".join(two_way.split(" <=> "))
    yield " -> ".join(reversed(two_way.split(" <=> ")))


def _parse_reaction(graph: object, derivation: str):
    sources, _, targets = derivation.partition(" -> ")
    return graph.findEdge(_get_side_vertices(graph, sources), _get_side_vertices(graph, targets))


def parse(abstract_system: 'dgODESystem', reaction: str) -> Union[object, Tuple[object,object]]:
    if reaction.find(" <=> ") != -1:
        first_reaction, second_reaction = _break_two_way_deviations(reaction)
        return _parse_reaction(abstract_system.graph, first_reaction), \
               _parse_reaction(abstract_system.graph, second_reaction)

    elif reaction.find(' -> ') != -1:
        return _parse_reaction(abstract_system.graph, reaction)