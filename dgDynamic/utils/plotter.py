import matplotlib.pyplot as pyplt
import time
import math


def plot(x_data, y_data, symbols, ignored, title,
         filename=None, labels=None, figure_size=None, axis_labels=None, axis_limits=None):
    """
    Tries to plot the data using the MatPlotLib
    :return: self (chaining enabled)
    """

    print("Started on plotting")
    if len(y_data) == 0 or len(x_data) == 0:
        raise ValueError("No or mismatched data")

    # let get a subplot that fill the whole figure area
    plt = pyplt.subplot(111)

    print("parsing data to matplotlib...")
    start_t = time.time()
    lines = plt.plot(x_data, y_data)
    end_t = time.time()
    print("matplotlib parsed. Took {} secs".format(end_t - start_t))

    pyplt.tight_layout()

    if axis_limits is not None:
        assert isinstance(axis_limits, (tuple, list))
        assert len(axis_limits) == 2
        plt.set_ylim(axis_limits[1])
        plt.set_xlim(axis_limits[0])

    if axis_labels is not None:
        assert isinstance(axis_labels, (tuple, list))
        assert len(axis_labels) >= 2
        assert isinstance(axis_labels[0], str) and isinstance(axis_labels[1], str)
        plt.xlabel(axis_labels[0])
        plt.ylabel(axis_labels[1])

    if labels is not None:
        assert len(labels) >= len(lines)
    else:
        labels = symbols

    for index, line in enumerate(lines):
        if index in ignored:
            line.remove()
        else:
            line.set_label(labels[index])
        if 20 < index <= 30:
            line.set_linestyle('dashed')
        elif 30 < index <= 40:
            line.set_linestyle('dashdot')
        elif 40 < index <= 50:
            line.set_linestyle('dotted')

    # shrinking the box so there is space for the left box
    box = plt.get_position()
    plt.set_position([box.x0, box.y0, box.width * 0.84, box.height])
    _, labels = plt.get_legend_handles_labels()

    plt.legend(loc='center left', bbox_to_anchor=(1, 0.5), ncol=math.ceil(len(labels) / 32.))

    print("Labels are set")

    if figure_size is not None:
        assert len(figure_size) >= 2

        def cm2inch(number): return number / 2.54

        fig = pyplt.gcf()
        fig.set_size_inches(cm2inch(figure_size[0]), cm2inch(figure_size[1]), forward=True)

    pyplt.title(title)
    if filename is None or type(filename) is not str:
        pyplt.show()
    else:
        pyplt.savefig(filename, bbox_inches='tight')

    print("Done plotting.")
