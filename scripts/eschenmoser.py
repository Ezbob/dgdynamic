from dgDynamic import dgDynamicSim, HyperGraph, show_plots
import random
import numpy as np
import enum

rate_std_deviation = np.nextafter(1, 0)
rate_mean = 0


class ImportantSpecies(enum.Enum):
    HCN = "HCN"
    Glyoxylate = "Glyoxylate"
    Oxaloglycolate = "Oxaloglycolate"
    Oxoaspartate = "Oxoaspartate"


reactions = [
    # Starting with the first autocatalytic cycle (on the green side)
    "2 {} -> C1S1".format(ImportantSpecies.HCN.name),
    "C1S1 -> C1S2",
    "C1S2 + {} -> C1S3".format(ImportantSpecies.Glyoxylate.name),
    "C1S3 -> C1S4",
    "C1S4 -> C1S5",
    "C1S5 -> C1S6 + {}".format(ImportantSpecies.Glyoxylate.name),
    "C1S6 -> {}".format(ImportantSpecies.Glyoxylate.name),
    # Next autocatalytic cycle (on the orange side)
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

r = generate_rates(len(reactions))

print(r)
parameters = {key: val for key, val in zip(reactions, r)}

initial_conditions = {
    ImportantSpecies.HCN.name: 10,
    ImportantSpecies.Glyoxylate.name: 2
}

print("Parameters are: ")
for react, param in parameters.items():
    print("{} : {}".format(react, param))

dg = HyperGraph.from_abstract(*reactions)

dg.print()

stochastic = dgDynamicSim(dg, "stochastic")

with stochastic('stochkit2') as stochkit2:
    stochkit2.trajectories = 10
    sim_range = (200, 100)
    out = stochkit2.simulate(sim_range, initial_conditions, parameters)

    out.plot()

show_plots()
