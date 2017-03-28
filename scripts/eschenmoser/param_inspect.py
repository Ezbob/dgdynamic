import mod
import dgDynamic
import datetime
import os.path

parameters = {
    'C1S2 -> C1S1': 0.80138722776345406, 'C1S5 -> C1S6 + Glyoxylate': 0.272057846003532,
    'C2S10 -> C2S9': 0.34434663881876759, 'C1S4 -> C1S5': 0.33503420067512013,
    'C1S6 + Glyoxylate -> C1S5': 0.071632378492243354,
    'C2S4 -> C2S5': 0.76931801050136162, 'C1S3 -> C1S2 + Glyoxylate': 0.071222510478821444,
    'C2S3 -> Oxaloglycolate + Oxoaspartate': 0.56634415174740382,
    'C1S2 + Glyoxylate -> C1S3': 0.65850119368837678,
    'C1S1 -> C1S2': 0.88911551518784304,
    'C2S6 -> Oxoaspartate': 0.65820176450975443,
    'C2S8 -> C2S7': 0.69604911168205519,
    'C2S10 + Glyoxylate -> C2S1': 0.8119440672973165,
    'C2S2 -> C2S1': 0.76052656858096035,
    'C2S6 -> C2S5': 0.35284877763735778,
    'C2S2 -> C2S3': 0.25279560531067857,
    'Oxaloglycolate + Oxoaspartate -> C2S3': 0.57471569997067595,
    'C2S1 -> C2S10 + Glyoxylate': 0.024686628337018068,
    'C2S7 -> C2S8': 0.44348052691871898,
    'C2S7 -> Glyoxylate + C2S6': 0.75291622891505483,
    'C2S5 -> C2S4': 0.98376013451151323,
    'Oxoaspartate -> C2S6': 0.10454718540998564,
    'C2S4 -> Oxaloglycolate': 0.32919292157653912,
    'C1S5 -> C1S4': 0.39459130158079425,
    'Glyoxylate -> C1S6': 0.87758942966204589,
    'C1S3 -> C1S4': 0.23654468480369395,
    'Oxaloglycolate -> C2S4': 0.69933577281251835,
    'C1S6 -> Glyoxylate': 0.70921664373389859,
    'C2S1 -> C2S2': 0.26071285452664594,
    'C2S9 -> C2S10': 0.84020639785765339,
    'C1S4 -> C1S3': 0.20863708493460942,
    '2 HCN -> C1S1': 0.074869936229712497,
    'C2S5 -> C2S6': 0.89862804304223598,
    'C1S1 -> 2 HCN': 0.24653873182694142,
    'C2S9 -> C2S8': 0.57622905334553642,
    'Glyoxylate + C2S6 -> C2S7': 0.30649682611654439,
    'C2S3 -> C2S2': 0.2861163900672723,
    'C2S8 -> C2S9': 0.76354189839622499
}

stoch_sim_range = (60000, 3000)
ode_sim_range = (0, 60000)
period_bounds = (600, stoch_sim_range[0] / 2)
method_name = "tauleaping"
output_dir = 'images'

initial_conditions = {
    'HCN': 2,
    'Glyoxylate': 2,
    'Oxaloglycolate': 1,
}

drain_params = {
    'HCN': {
        'in': {
            'constant': 0.1
        },
        'out': {
            'factor': 0.0001
        }
    },
    'Glyoxylate': {
        'in': {
            'constant': 0.002
        },
        'out': {
            'factor': 0.0001
        }
    },
    'Oxaloglycolate': {
        'out': {
            'factor': 0.002
        }
    }
}

dg = dgDynamic.HyperGraph.from_abstract(*tuple(parameters.keys()))
dg.print()

ode = dgDynamic.dgDynamicSim(dg)
stochastic = dgDynamic.dgDynamicSim(dg, 'stochastic')

with stochastic('stochkit2') as stochkit2:

    stochkit2.method = method_name
    stochkit2.trajectories = 10
    outs = stochkit2(stoch_sim_range, initial_conditions, parameters, drain_params)

    for out in outs:
        analytics = dgDynamic.DynamicAnalysisDevice(out)

        variance_measurement = analytics.variance_oscillation_measure()
        fourier_measurement = analytics.fourier_oscillation_measure(period_bounds[0], period_bounds[1])

        dt = "{:%Y%m%d%H%M%S}".format(datetime.datetime.now())
        title = "{} {} - var: {}, four: {}" \
            .format(out.solver_used.name, method_name, variance_measurement, fourier_measurement)

        image_path = os.path.join(output_dir, "eschenmoser_{}_{}_plot_{}.png".format(out.solver_used.name, method_name, dt))
        out.plot(filename=image_path, figure_size=(46, 24), title=title)
