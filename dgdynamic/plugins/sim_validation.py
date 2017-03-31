

def simulation_parameter_validate(end_t, initial_conditions, rates_params, drain_params):
    assert isinstance(end_t, (int, float)), "End_t must be a float or int"
    assert end_t > 0, "End_t most be a positive number"
    assert isinstance(initial_conditions, dict), "Expected {} got {} for initial conditions"\
        .format(dict, type(rates_params))
    assert isinstance(rates_params, dict), "Expected {} got {} for rate parameters".format(dict, type(rates_params))
    if drain_params is not None:
        assert isinstance(drain_params, dict), "Expected {} got {} for drain parameters"\
            .format(dict, type(rates_params))
