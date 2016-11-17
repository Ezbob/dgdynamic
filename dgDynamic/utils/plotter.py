import matplotlib.pyplot as pyplt
import math


def plot(input_data):
    """
    Tries to plot the data using the MatPlotLib
    :return: self (chaining enabled)
    """
    pyplt.figure()

    x_data, y_data = input_data['independent'], input_data['dependent']

    def get_input(field):
        if field in input_data:
            return input_data[field]
        return None

    if len(y_data) == 0 or len(x_data) == 0:
        return

    # let get a subplot that fill the whole figure area
    plt = pyplt.subplot(111)

    lines = plt.plot(x_data, y_data)

    pyplt.tight_layout()

    axis_limits = get_input('axis_limits')
    if axis_limits is not None:
        assert isinstance(axis_limits, (tuple, list))
        assert len(axis_limits) == 2
        plt.set_ylim(axis_limits[1])
        plt.set_xlim(axis_limits[0])

    axis_labels = get_input('axis_labels')
    if axis_labels is not None:
        assert isinstance(axis_labels, (tuple, list))
        assert len(axis_labels) >= 2
        assert isinstance(axis_labels[0], str) and isinstance(axis_labels[1], str)
        plt.xlabel(axis_labels[0])
        plt.ylabel(axis_labels[1])

    symbols = get_input('symbols')
    if symbols is not None:
        labels = get_input('labels')
        if labels is not None:
            assert len(input_data['labels']) >= len(lines)
        else:
            labels = symbols

        for index, line_labels in enumerate(zip(lines, labels)):
            ignored = input_data['ignored']
            if index in ignored:
                line_labels[0].remove()
            else:
                line_labels[0].set_label(line_labels[1])
            if 20 < index <= 30:
                line_labels[0].set_linestyle('dashed')
            elif 30 < index <= 40:
                line_labels[0].set_linestyle('dashdot')
            elif 40 < index <= 50:
                line_labels[0].set_linestyle('dotted')

        # shrinking the box so there is space for the left box
        box = plt.get_position()
        plt.set_position([box.x0, box.y0, box.width * 0.84, box.height])
        _, labels = plt.get_legend_handles_labels()
        plt.legend(loc='center left', bbox_to_anchor=(1, 0.5), ncol=math.ceil(len(labels) / 32.))

    figure_size = get_input('figure_size')
    if figure_size is not None:
        assert len(figure_size) >= 2

        def cm2inch(number): return number / 2.54

        fig = pyplt.gcf()
        fig.set_size_inches(cm2inch(figure_size[0]), cm2inch(figure_size[1]), forward=True)

    title = get_input('title')
    if title is not None:
        pyplt.title(title)

    filename = get_input('filename')
    if filename is not None and type(filename) is str:
        pyplt.savefig(filename, bbox_inches='tight')

