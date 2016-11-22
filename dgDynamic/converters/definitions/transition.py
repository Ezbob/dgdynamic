import mod


class TransitionChannel:
    solutions = ()

    def __init__(self, rate_id, is_input, channel_edge=None, is_decay=False):
        self.channel_edge = channel_edge
        self.rate_id = rate_id
        self.is_input = is_input
        self.is_decay = is_decay

    def __repr__(self):
        if self.is_decay:
            return "<delay channel@r{} to {}>".format(self.rate_id, self.solutions)
        elif self.is_input:
            return "<input channel{0}@r{0} to {1}>".format(self.rate_id, self.solutions)
        else:
            return "<output channel{0}@r{0} to {1}>".format(self.rate_id, self.solutions)

    def add_reagents(self, reagents):
        for target in reagents:
            if isinstance(target, mod.DGVertex):
                self.solutions += (target.graph.name,)
            else:
                self.solutions += (target,)
        return self
