import config


class ParserNode:
    pass


class Num(ParserNode):
    value = None


class Id(ParserNode):
    id = None


class Op(ParserNode):
    symbol = None
    operator = None


class Add(ParserNode):
    left = None
    op = None
    right = None


class Mul(ParserNode):
    left = None
    op = None
    right = None


class Func(ParserNode):
    name = None
    args = None
