"""
    Chemical Ground Form
"""
import mod


class Channel:
    solutions = ()

    def __init__(self, rate, is_input, channel_name='', is_decay=False):
        self.channel_name = channel_name
        self.rate = rate
        self.is_input = is_input
        self.is_decay = is_decay

    def __repr__(self):
        if self.is_decay:
            return "<channel {}@{};{}>".format("τ", self.rate, self.solutions)
        elif self.is_input:
            return "<channel ?{}@{};{}>".format(self.channel_name, self.rate, self.solutions)
        else:
            return "<channel !{}@{};{}>".format(self.channel_name, self.rate, self.solutions)

    def add_reagents(self, reagents):
        for target in reagents:
            if isinstance(target, mod.mod_.DGVertex):
                self.solutions += (target.graph.name,)
            else:
                self.solutions += (target,)
        return self
