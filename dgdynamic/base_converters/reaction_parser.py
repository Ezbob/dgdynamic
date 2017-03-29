from dgdynamic.utils.exceptions import ReactionParseError
from ..utils.project_utils import log_it
from collections import namedtuple
from io import StringIO


def _parse_sides(side):
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
                    raise ReactionParseError("Index error in\
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


def _get_side_vertices(graph, side):
    for sym in _parse_sides(side):
        for vertex in graph.vertices:
            if vertex.graph.name == sym:
                yield vertex


def _break_two_way_deviations(two_way):
    yield " -> ".join(two_way.split(" <=> "))
    yield " -> ".join(reversed(two_way.split(" <=> ")))


def _parse_mod_reaction(graph, derivation):
    sources, _, targets = derivation.partition(" -> ")

    edge = graph.findEdge(_get_side_vertices(graph, sources), _get_side_vertices(graph, targets))
    is_null = edge.isNull() if hasattr(edge, "isNull") else False

    if is_null or edge is None:
        raise ReactionParseError("No edge for reaction: {}".format(derivation))
    return edge


@log_it
def abstract_mod_parser(deviation_graph, reaction):

    parse_result = namedtuple('parse_result', 'mod_edges representation has_inverse')
    if reaction.find(" <=> ") != -1:
        first_reaction, second_reaction = _break_two_way_deviations(reaction)
        result = (_parse_mod_reaction(deviation_graph, first_reaction),
                  _parse_mod_reaction(deviation_graph, second_reaction))
        return parse_result(mod_edges=result, representation=reaction, has_inverse=True)

    elif reaction.find(' -> ') != -1:
        result = (_parse_mod_reaction(deviation_graph, reaction),)
        return parse_result(mod_edges=result, representation=reaction, has_inverse=False)
    else:
        raise ReactionParseError("Unknown reaction format for reaction: {}".format(reaction))


def hyper_edge_to_string(edge, add_newline=True):
    with StringIO() as out:
        for index, source_vertex in enumerate(edge.sources):
            out.write(source_vertex.graph.name)
            if index < edge.numSources - 1:
                out.write(" + ")
        out.write(" -> ")

        for index, target_vertex in enumerate(edge.targets):
            out.write(target_vertex.graph.name)
            if index < edge.numTargets - 1:
                out.write(" + ")
        if add_newline:
            out.write("\n")
        return out.getvalue()
