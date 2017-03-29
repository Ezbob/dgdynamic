import io
import dgdynamic.base_converters.convert_base as base
from dgdynamic.config.settings import config
from dgdynamic.utils.exceptions import ModelError

INDENT_SPACES = 4


def i(message, level):
    return "{}{}".format(_indent(level), message)


def _indent(indent_level):
    return ' ' * (indent_level * INDENT_SPACES)


def _mass_action_reaction(stream, reaction_id, rate, reactants, products, float_precision=18, indent=0):
    stream.write(i('<Reaction>\n', indent))
    stream.write(i('<Id>{}</Id>\n'.format(reaction_id), indent + 1))
    stream.write(i('<Type>mass-action</Type>\n', indent + 1))
    if isinstance(rate, float):
        stream.write(i('<Rate>{:.{}f}</Rate>\n'.format(rate, float_precision), indent + 1))
    else:
        stream.write(i('<Rate>{}</Rate>\n'.format(rate), indent + 1))
    stream.write(i('<Reactants>\n', indent + 1))
    for reactant in reactants:
        react_id, stoichiometry = reactant
        stream.write(i('<SpeciesReference id="{}" stoichiometry="{}"/>\n'.format(
            react_id, stoichiometry
        ), indent + 2))
    stream.write(i('</Reactants>\n', indent + 1))
    stream.write(i('<Products>\n', indent + 1))
    for product in products:
        product_id, stoichiometry = product
        stream.write(i('<SpeciesReference id="{}" stoichiometry="{}"/>\n'.format(
            product_id, stoichiometry
        ), indent + 2))
    stream.write(i('</Products>\n', indent + 1))
    stream.write(i('</Reaction>\n', indent))


def _custom_reaction(stream, reaction_id, propensity_function, reactants, products, indent=0):
    stream.write(i('<Reaction>\n', indent))
    stream.write(i('<Id>{}</Id>\n'.format(reaction_id), indent + 1))
    stream.write(i('<Type>customized</Type>\n', indent + 1))
    stream.write(i('<PropensityFunction>{}</PropensityFunction>\n'.format(propensity_function), indent + 1))
    stream.write(i('<Reactants>\n', indent + 1))
    for reactant in reactants:
        react_id, stoichiometry = reactant
        stream.write(i('<SpeciesReference id="{}" stoichiometry="{}"/>\n'.format(
            react_id, stoichiometry
        ), indent + 2))
    stream.write(i('</Reactants>\n', indent + 1))
    stream.write(i('<Products>\n', indent + 1))
    for product in products:
        product_id, stoichiometry = product
        stream.write(i('<SpeciesReference id="{}" stoichiometry="{}"/>\n'.format(
            product_id, stoichiometry
        ), indent + 2))
    stream.write(i('</Products>\n', indent + 1))
    stream.write(i('</Reaction>\n', indent))


def _species_initial_condition(stream, species_id, initial_value, indent=0):
    stream.write(i('<Species>\n', indent))
    stream.write(i('<Id>{}</Id>\n'.format(species_id), indent + 1))
    stream.write(i('<InitialPopulation>{}</InitialPopulation>\n'.format(initial_value), indent + 1))
    stream.write(i('</Species>\n', indent))


def generate_model(simulator, initial_conditions, rate_parameters, drain_parameters=None):

    total_reactions = simulator.reaction_count

    if drain_parameters is not None:
        drain_values = dict(base.get_drain_rate_dict(simulator.internal_drain_dict, drain_parameters))
        total_reactions += sum(1 if val > 0 else 0 for val in drain_values.values())

    initial_values = base.get_initial_values(initial_conditions, simulator.symbols)
    precision = config.getint('Simulation', 'FIXED_POINT_PRECISION', fallback=18)
    translate_dict = {sym: internal.replace('$', '') for sym, internal in simulator.internal_symbol_dict.items()}

    def build_drain_equation():
        # Drains are by it's nature a elementary reaction with LHS stoiciometric 1
        for vertex in simulator.graph.vertices:
            in_offset, in_factor, out_offset, out_factor = simulator.internal_drain_dict[vertex.graph.name]
            in_offset_val, in_factor_val, out_offset_val, out_factor_val = drain_values[in_offset.replace('$', '')], \
                drain_values[in_factor.replace('$', '')], drain_values[out_offset.replace('$', '')], \
                drain_values[out_factor.replace('$', '')]

            if in_offset_val > 0 or in_factor_val > 0:
                in_propensity = "{:.{}f}*{}+{:.{}f}".format(in_factor_val, precision,
                                                            translate_dict[vertex.graph.name],
                                                            in_offset_val, precision)
                yield in_propensity, tuple(), ((translate_dict[vertex.graph.name].replace('$', ''), 1),)

            if out_offset_val > 0 or out_factor_val > 0:
                out_propensity = "{:.{}f}*{}+{:.{}f}".format(out_factor_val, precision,
                                                             translate_dict[vertex.graph.name],
                                                             out_offset_val, precision)
                yield out_propensity, ((translate_dict[vertex.graph.name].replace('$', ''), 1),), tuple()

    def build_rate_equations():

        def check_and_build_stoichiometry(stoichio_dict, trans_dict):
            # Reactions with order > 3 (on the LHS) are not supported
            for label, stoichio in stoichio_dict.items():
                if stoichio > 3:
                    raise ModelError("Species {!r} has stoichiometry {}. Reactions with order > 3 are not supported by "
                                     "StochKit2."
                                     .format(label, stoichio))
                yield trans_dict[label], stoichio

        rate_dict = dict(base.get_edge_rate_dict(simulator.graph, rate_parameters))
        for edge in simulator.graph.edges:
            source_stoichio, target_stoichio = simulator.edge_stoichiometrics(edge)
            translated_source_stoichio = tuple(check_and_build_stoichiometry(source_stoichio, translate_dict))
            translated_target_stoichio = tuple((translate_dict[label], stoichio)
                                               for label, stoichio in target_stoichio.items())
            yield rate_dict[edge.id], translated_source_stoichio, translated_target_stoichio

    with io.StringIO() as model_string:
        model_string.write('<!-- StochKit2 model generated by dgDynamic -->\n')
        model_string.write('<Model>\n')
        generate_preamble(model_string, total_reactions, simulator.species_count, indent=1)
        generate_rate_equations(model_string, build_rate_equations(),
                                build_drain_equation() if drain_parameters is not None else tuple(),
                                precision=precision, indent=1)
        generate_species_list(model_string,
                              zip((sym.replace('$', '') for sym in simulator.symbols_internal), initial_values),
                              indent=1)
        model_string.write('</Model>\n')
        return model_string.getvalue()


def generate_preamble(stream, reaction_count, species_count, indent=0):
    stream.write(i("<NumberOfReactions>{}</NumberOfReactions>\n".format(reaction_count), indent))
    stream.write(i("<NumberOfSpecies>{}</NumberOfSpecies>\n".format(species_count), indent))


def generate_rate_equations(stream, reactions, drains, precision=18, indent=0):

    stream.write(i('<ReactionsList>\n', indent))
    for index, r in enumerate(reactions):
        rate, reactants, products = r
        _mass_action_reaction(stream, "R{}".format(index), rate, reactants, products,
                              float_precision=precision, indent=indent + 1)

    for index, d in enumerate(drains):
        propensity_function, reactants, products = d
        _custom_reaction(stream, "D{}".format(index), propensity_function, reactants, products, indent=indent + 1)

    stream.write(i('</ReactionsList>\n', indent))


def generate_species_list(stream, species, indent=0):
    stream.write(i('<SpeciesList>\n', indent))
    for s in species:
        species_id, initial_value = s
        _species_initial_condition(stream, species_id, initial_value, indent=indent + 1)
    stream.write(i('</SpeciesList>\n', indent))
