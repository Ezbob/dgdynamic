import matplotlib.pyplot as plt
import sys

if __name__ == "__main__":
    if len(sys.argv) == 3 and (sys.argv[1] is not None or sys.argv[2] is not None):
        ys = list(eval(sys.argv[1]))
        ts = list(eval(sys.argv[2]))
        plt.plot(ts, ys)
        plt.show()

