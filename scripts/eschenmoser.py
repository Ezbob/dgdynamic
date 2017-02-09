from dgDynamic import dgDynamicSim, HyperGraph, show_plots
import random
import numpy as np

rate_std_deviation = np.nextafter(1, 0)
rate_mean = 0

reacts = [
    "4 HCN -> 2 N2H",
    #"HCN + HCN -> HCN'",
    "2 N2H -> 2 NOHNH2"
]


def random_rates(n, mean=0, std_deviation=1):
    for i in range(n):
        rand = random.gauss(mean, std_deviation)
        if rand < 0.0:
            rand = abs(rand)
        yield rand


r = tuple(random_rates(len(reacts), rate_mean, rate_std_deviation))

parameters = {key: val for key, val in zip(reacts, r)}

initial_conditions = {
    'HCN': 10,
    'N2H': 4,
    'NOHNH2': 2
}

print("Parameters are: ")
for react, param in parameters.items():
    print("{} : {}".format(react, param))

dg = HyperGraph.from_abstract(*reacts)

stochastic = dgDynamicSim(dg, "stochastic")

with stochastic('stochkit2') as stochkit2:
    stochkit2.trajectories = 10
    sim_range = (200, 100)
    out = stochkit2.simulate(sim_range, initial_conditions, parameters)

    out.plot()


show_plots()
