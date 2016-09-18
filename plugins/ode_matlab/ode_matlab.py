##
#  Matlab ode solver plugin
#  This plugin uses the matlab python engine to approximate solutions to ODEs
##
import sys

if __name__ != "__main__":
    import matlab.engine

    engine = matlab.engine.start_matlab()

else:
    print("Plugin not meant as standalone application", file=sys.stderr)


def stop_engine():
    global engine
    engine.quit()


def create_matlab_func(ode_func):
    pass


def set_ode_solver(solver_name):
    pass
