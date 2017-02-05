from dgDynamic.plugins.stochastic.stochastic_plugin import StochasticPlugin
from dgDynamic.choices import SupportedStochasticPlugins, StochKit2StochasticSolvers
from .stochkit2_converter import generate_model
from dgDynamic.output import SimulationOutput
import enum
import subprocess
import re
import array
import tempfile
import dgDynamic.utils.messages as messages
import dgDynamic.config.settings as settings
import os.path as path
import dgDynamic.utils.exceptions as util_exceptions

name = SupportedStochasticPlugins.StochKit2
this_dir = path.abspath(path.dirname(__file__))


class StochKit2Stochastic(StochasticPlugin):

    def __init__(self, simulator, stochastic_method=StochKit2StochasticSolvers.direct, timeout=None, trajectories=1):
        super().__init__(simulator, timeout)
        self._method = stochastic_method
        self.tau_leaping_epsilon = 0.03
        self.switch_threshold = 10
        self._trajectories = abs(int(trajectories))
        self.stochkit2_path = settings.config.get('Simulation', 'STOCHKIT2_PATH', fallback='')
        if self.stochkit2_path == '':
            self.stochkit2_path = path.join(this_dir, 'StochKit')
        else:
            self.stochkit2_path = path.abspath(self.stochkit2_path)

    def model(self, initial_conditions, rate_parameters, drain_parameters=None):
        return generate_model(self._simulator, initial_conditions, rate_parameters, drain_parameters)

    @property
    def method(self):
        if isinstance(self._method, enum.Enum):
            return self._method
        elif isinstance(self._method, str):
            for supported in StochKit2StochasticSolvers:
                name, value = supported.name.lower().strip(), supported.value.lower().strip()
                user_method = self._method.lower().strip()
                if user_method == name or user_method == value:
                    return supported

    @property
    def flag_options(self):
        flags = ['--no-stats', '--keep-trajectories', '--label', '-f']
        return flags

    @method.setter
    def method(self, value):
        self._method = value

    @property
    def trajectories(self):
        return self._trajectories

    @trajectories.setter
    def trajectories(self, value):
        self._trajectories = abs(int(value))

    def simulate(self, simulation_range, initial_conditions, rate_parameters, drain_parameters, *args, **kwargs):
        end_time, sample_number = int(simulation_range[0]), int(simulation_range[1])
        model_filename = "model.xml"
        output_dirname = "model_output"

        def read_output(filepath):
            independent = array.array('d')
            dependent = tuple()
            label_translator = {v.replace('$', ''): k for k, v in self._simulator.internal_symbol_dict.items()}
            with open(filepath, mode="r") as rfile:
                white_space = re.compile(r"\s+")
                header = white_space.split(next(rfile).strip())
                for line in rfile:
                    splitted = array.array('d', map(float, white_space.split(line.strip())))
                    independent.append(splitted[:1][0])
                    dependent += (splitted[1:],)
            return tuple(label_translator[sym] for sym in header[1:]), independent, dependent

        self.logger.info("started on StochKit2 simulation")

        with tempfile.TemporaryDirectory() as tmp_dir:
            model_path = path.join(tmp_dir, model_filename)
            model = self.model(initial_conditions, rate_parameters, drain_parameters)

            self.logger.info("Stochkit2 model:\n{}".format(model))
            with open(model_path, mode="w") as model_file:
                model_file.write(model)

            if self.method == StochKit2StochasticSolvers.direct:
                program_name = "ssa"
            elif self.method == StochKit2StochasticSolvers.tauLeaping:
                program_name = "tau_leaping"
            else:
                raise util_exceptions.SimulationError("Unknown stochkit2 method selected")

            program_path = path.join(self.stochkit2_path, program_name)
            self.logger.info("Using stochkit2 driver at {}".format(program_name))
            execution_args = [program_path, '-m {}'.format(model_path),
                              '-r {}'.format(self.trajectories), '-t {}'.format(end_time,),
                              '-i {}'.format(sample_number),
                              '--epsilon {}'.format(self.tau_leaping_epsilon),
                              '--threshold {}'.format(self.switch_threshold),
                              *self.flag_options]
            self.logger.info("Execution arguments are {!r}".format(" ".join(execution_args)))

            try:
                completed = subprocess.run(" ".join(execution_args), shell=True, timeout=self.timeout,
                                           stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                self.logger.info(completed.stdout)
            except subprocess.TimeoutExpired as exception:
                messages.print_solver_done(name, self.method.name, was_failure=True)
                # TODO check if partial output is available
                return SimulationOutput(name, (0, simulation_range[0]), self._simulator.symbols,
                                        solver_method=self.method, errors=(exception,))
            if completed.returncode != 0:
                exception = util_exceptions.SimulationError("Error in simulation: {}".format(completed.stdout))
                messages.print_solver_done(name, self.method.name, was_failure=True)
                return SimulationOutput(name, (0, simulation_range[0]), self._simulator.symbols,
                                        solver_method=self.method, errors=(exception,))
            output_trajectories = path.join(tmp_dir, output_dirname, 'trajectories')

            messages.print_solver_done(name, method_name=self.method.name)
            if self.trajectories == 1:
                self.logger.info("Collecting output from single trajectory")
                header, independent, dependent = read_output(path.join(output_trajectories,
                                                                       'trajectory{}.txt'.format(0)))

                return SimulationOutput(name, (0, simulation_range[0]), header, independent=independent,
                                        dependent=dependent, solver_method=self.method)
            else:
                self.logger.info("Collecting output from {} trajectories".format(self.trajectories))
                trajectories = tuple()
                for i in range(self.trajectories):
                    header, independent, dependent = read_output(path.join(output_trajectories,
                                                                           'trajectory{}.txt'.format(i)))

                    trajectories += (SimulationOutput(name, (0, simulation_range[0]), header,
                                                      independent=independent, dependent=dependent,
                                                      solver_method=self.method),)
                return trajectories
