import unittest

from dgDynamic.plugins.ode.matlab.matlab_converter import get_matlab_lambda
from dgDynamic.plugins.ode.scipy.scipy_converter import get_scipy_lambda
from dgDynamic.simulators.ode_simulator import ODESystem
from dgDynamic.structures import HyperGraph


class ConverterTestCase(unittest.TestCase):

    def setUp(self):
        self.first_eq = "A + B -> C"
        self.second_eq = "B + C <=> D"
        self.dg = HyperGraph.from_abstract(
            self.first_eq,
            self.second_eq,
        )
        self.sim = ODESystem(self.dg)
        self.parameters = {
            self.first_eq: {'->': 2},
            self.second_eq: {'<-': 4, '->': 2},
        }
        self.drain_rates = {
            'A': {'in': 2, 'out': 2}
        }

    def test_scipy_lambda_construction_dict(self):

        func = get_scipy_lambda(self.sim, parameter_substitutions=self.parameters,
                                drain_substitutions=self.drain_rates)
        self.assertEqual(func, "lambda t,y: [2*y[0] - 2*y[0] - y[0]*y[1]*2, 0.0*y[1] - 0.0*y[1] - y[0]*y[1]*2 - "
                               "y[1]*y[2]*2 + y[3]*4, 0.0*y[2] - 0.0*y[2] + y[0]*y[1]*2 - y[1]*y[2]*2 + y[3]*4, "
                               "0.0*y[3] - 0.0*y[3] + y[1]*y[2]*2 - y[3]*4, ]")

    def test_matlab_construction_dict(self):
        func = get_matlab_lambda(self.sim, parameter_substitutions=self.parameters,
                                 drain_substitutions=self.drain_rates)
        self.assertEqual(func, "@(t,y) [2*y(1) - 2*y(1) - y(1)*y(2)*2; 0.0*y(2) - 0.0*y(2) - y(1)*y(2)*2 - "
                               "y(2)*y(3)*2 + y(4)*4; 0.0*y(3) - 0.0*y(3) + y(1)*y(2)*2 - y(2)*y(3)*2 + y(4)*4; "
                               "0.0*y(4) - 0.0*y(4) + y(2)*y(3)*2 - y(4)*4; ]")

if __name__ == "__main__":
    unittest.main()
