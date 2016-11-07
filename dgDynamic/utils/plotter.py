import matplotlib.pyplot as pyplt
import math


def plot(queue):
    """
    Tries to plot the data using the MatPlotLib
    :return: self (chaining enabled)
    """
    pyplt.figure()
    input_data = queue.get()

    x_data, y_data = input_data['independent'], input_data['dependent']

    def get_input(field):
        if field in input_data:
            return input_data[field]
        return None

    if len(y_data) == 0 or len(x_data) == 0:
        raise ValueError("No or mismatched data")

    # let get a subplot that fill the whole figure area
    plt = pyplt.subplot(111)

    lines = plt.plot(x_data, y_data)

    pyplt.tight_layout()

    if get_input('axis_limits') is not None:
        axis_limits = input_data['axis_limits']
        assert isinstance(axis_limits, (tuple, list))
        assert len(axis_limits) == 2
        plt.set_ylim(axis_limits[1])
        plt.set_xlim(axis_limits[0])

    if get_input('axis_labels') is not None:
        axis_labels = input_data['axis_labels']
        assert isinstance(axis_labels, (tuple, list))
        assert len(axis_labels) >= 2
        assert isinstance(axis_labels[0], str) and isinstance(axis_labels[1], str)
        plt.xlabel(axis_labels[0])
        plt.ylabel(axis_labels[1])

    if get_input('symbols') is not None:
        if get_input('labels') is not None:
            assert len(input_data['labels']) >= len(lines)
            labels = input_data['labels']
        else:
            labels = input_data['symbols']

        for index, line in enumerate(lines):
            if index in input_data['ignored']:
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

    if get_input('figure_size') is not None:
        figure_size = input_data['figure_size']
        assert len(figure_size) >= 2

        def cm2inch(number): return number / 2.54

        fig = pyplt.gcf()
        fig.set_size_inches(cm2inch(figure_size[0]), cm2inch(figure_size[1]), forward=True)

    if get_input('title') is not None:
        pyplt.title(input_data['title'])
    filename = get_input('filename')
    if filename is None or type(filename) is not str:
        pyplt.show()
    else:
        pyplt.savefig(filename, bbox_inches='tight')

