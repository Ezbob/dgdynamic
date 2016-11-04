"""
    Chemical Ground Form
"""
import mod


class Channel:
    solutions = ()

    def __init__(self, rate, is_input, channel_edge=None, is_decay=False):
        self.channel_edge = channel_edge
        self.rate = rate
        self.is_input = is_input
        self.is_decay = is_decay

    def __repr__(self):
        if self.is_decay:
            return "<channel τ@r{};{}>".format(self.rate, self.solutions)
        elif self.is_input:
            return "<channel ?c{0}@r{0};{1}>".format(self.rate, self.solutions)
        else:
            return "<channel !c{0}@r{0};{1}>".format(self.rate, self.solutions)

    def add_reagents(self, reagents):
        for target in reagents:
            if isinstance(target, mod.mod_.DGVertex):
                self.solutions += (target.graph.name,)
            else:
                self.solutions += (target,)
        return self
