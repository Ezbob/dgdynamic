from dgDynamic import dgDynamicSim, HyperGraph, show_plots
import random
import numpy as np
import enum


class ImportantSpecies(enum.Enum):
    HCN = "HCN"
    Glyoxylate = "Glyoxylate"
    Oxaloglycolate = "Oxaloglycolate"
    Oxoaspartate = "Oxoaspartate"


cycle1_reactions = [
    "2 {} -> C1S1".format(ImportantSpecies.HCN.name),
    "C1S1 -> C1S2",
    "C1S2 + {} -> C1S3".format(ImportantSpecies.Glyoxylate.name),
    "C1S3 -> C1S4",
    "C1S4 -> C1S5",
    "C1S5 -> C1S6 + {}".format(ImportantSpecies.Glyoxylate.name),
    "C1S6 -> {}".format(ImportantSpecies.Glyoxylate.name),
]

cycle2_reactions = [
    "C2S10 + {} -> C2S1".format(ImportantSpecies.Glyoxylate.name),
    "C2S1 -> C2S2",
    "C2S2 -> C2S3",
    "C2S3 -> {} + {}".format(ImportantSpecies.Oxaloglycolate.name, ImportantSpecies.Oxoaspartate.name),
    "{} <=> C2S4".format(ImportantSpecies.Oxaloglycolate.name),
    "C2S4 <=> C2S5",
    "C2S5 <=> C2S6",
    "{} -> C2S6".format(ImportantSpecies.Oxoaspartate.name),
    "{} + C2S6 -> C2S7".format(ImportantSpecies.Glyoxylate.name),
    "C2S7 -> C2S8",
    "C2S8 -> C2S9",
    "C2S9 -> C2S10"
]

extras = [
    '{} -> {}'.format(ImportantSpecies.Oxaloglycolate.name, ImportantSpecies.HCN.name)
]

cycle1_hyper = HyperGraph.from_abstract(*cycle1_reactions)
cycle2_hyper = HyperGraph.from_abstract(*cycle2_reactions)

cycle1_hyper.print()
cycle2_hyper.print()

reactions = cycle1_reactions + cycle2_reactions  #+ extras


def generate_rates(number_of_reactions, decomposed_rates=()):
    results = [0.0] * number_of_reactions
    decomposed_args = []

    for decompose_set in decomposed_rates:
        # decomposition of "chain reactions" into elementary reactions yields probability k / p where p
        # are the number reactions that the decomposition yields
        rand = random.random() / len(decompose_set)
        for arg in decompose_set:
            results[arg] = rand
            decomposed_args.append(arg)

    for i in range(number_of_reactions):
        if i not in decomposed_args:
            results[i] = random.random()
    return results

for i in range(4):
    all_rates = generate_rates(len(reactions))
    parameters = {key: val for key, val in zip(reactions, all_rates)}

    initial_conditions = {
        ImportantSpecies.HCN.name: 2,
        #"C2S10": 1
        ImportantSpecies.Glyoxylate.name: 1,
        ImportantSpecies.Oxaloglycolate.name: 1,
        #ImportantSpecies.Oxoaspartate.name: 1
    }

    drain_params = {
        # 'C1S3': {
        #     'in': {
        #         'constant': 0.0001
        #     }
        # },
        # 'C2S6': {
        #     'out': {
        #         'factor': 0.1
        #     }
        # },
        # 'C2S10': {
        #    'out': {
        #        'factor': 0.001
        #    }
        # },
        ImportantSpecies.HCN.name: {
            'in': {
                'constant': 0.1
            },
            'out': {
                'factor': 0.1
            }
        },
        ImportantSpecies.Glyoxylate.name: {
            #'in': {
            #    'constant': 1e-6
            #}
            'out': {
                'factor': 0.002
            }
        },
        # ImportantSpecies.Oxaloglycolate.name: {
        #
        #     'out': {
        #         'factor': 0.00001
        #     },
        #     'in': {
        #         'constant': 0.01
        #     }
        # }
    }

    #parameters["C2S3 -> {} + {}".format(ImportantSpecies.Oxaloglycolate.name, ImportantSpecies.Oxoaspartate.name)] = 0.0001

    print("Parameters are: ")
    for react, param in parameters.items():
        print("{} : {}".format(react, param))

    dg = HyperGraph.from_abstract(*reactions)

    dg.print()

    #stochastic = dgDynamicSim(dg, "stochastic")
    ode = dgDynamicSim(dg)

    # with stochastic('stochkit2') as stochkit2:
    #     stochkit2.trajectories = 10
    #     sim_range = (200, 100)
    #     out = stochkit2.simulate(sim_range, initial_conditions, parameters, drain_params)
    #
    #     out.plot()

    with ode('scipy') as scipy:
        int_range = (0, 5000)
        #for i in range(10):
        scipy(int_range, initial_conditions, parameters, drain_params).plot(figure_size=(40, 20),
                                                                            axis_limits=((0, 1000), (0, 1.2))).show()

#show_plots()
