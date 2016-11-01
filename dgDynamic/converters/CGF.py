"""
    Chemical Ground Form
"""
import abc


class CGFEntity(abc.ABC):

    @abc.abstractmethod
    def is_null(self):
        pass


class Null(CGFEntity):
    def is_null(self):
        return True

    def __str__(self):
        return "<CGF Null>"


class Channel(CGFEntity):
    def is_null(self):
        return False

    def __init__(self, channel_name, rate, is_input, is_decay=False):
        self.channel_name = channel_name if not is_decay else "τ"
        self.rate = rate
        self.is_input = is_input
        self.is_decay = is_decay

    def __str__(self):
        if self.is_input:
            return "<channel ?{}@{}>".format(self.channel_name, self.rate)
        else:
            return "<channel !{}@{}".format(self.channel_name, self.rate)


class Molecule(CGFEntity):
    def is_null(self):
        return False

    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name


class CGF(CGFEntity):
    def is_null(self):
        return False
    reagents = dict()

