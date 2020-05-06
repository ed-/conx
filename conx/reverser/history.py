#!/usr/bin/env python

# Operations on a single history.
# A history is a nine-bit integer in the range [0..511].

DEAD = 0
ALIVE = 1

# Utility Functions.
ib = lambda i: int(bool(i))
cat = lambda b: sum([ib(v) << (len(b) - i - 1)
                     for i, v in enumerate(b)])

# Get a single cell from a history.
nw = lambda i: ib(i & 0400)
n  = lambda i: ib(i & 0200)
ne = lambda i: ib(i & 0100)
w  = lambda i: ib(i &  040)
c  = lambda i: ib(i &  020)
e  = lambda i: ib(i &  010)
sw = lambda i: ib(i &   04)
s  = lambda i: ib(i &   02)
se = lambda i: ib(i &   01)

# Shift a history one row in one direction and/or one column in any direction.
# Store these as they'll be reused a lot.
_NW, _N, _NE = {}, {}, {}
_W,  _C, _E  = {}, {}, {}
_SW, _S, _SE = {}, {}, {}

for i in range(01000):
    _NW[i] = cat([DEAD, DEAD,  DEAD,
                  DEAD, nw(i), n(i),
                  DEAD, w(i),  c(i)])

    _N[i]  = cat([DEAD,  DEAD, DEAD,
                  nw(i), n(i), ne(i),
                  w(i),  c(i), e(i)])

    _NE[i] = cat([DEAD, DEAD, DEAD,
                  DEAD, n(i), ne(i),
                  DEAD, c(i), e(i)])

    _W[i]  = cat([DEAD, nw(i), n(i),
                  DEAD, w(i),  c(i),
                  DEAD, sw(i), s(i)])

    _E[i]  = cat([DEAD, n(i), ne(i),
                  DEAD, c(i), e(i),
                  DEAD, s(i), se(i)])

    _SW[i] = cat([DEAD, DEAD,  DEAD,
                  DEAD, w(i),  c(i),
                  DEAD, sw(i), s(i)])

    _S[i]  = cat([DEAD,  DEAD, DEAD,
                  w(i),  c(i), e(i),
                  sw(i), s(i), se(i)])

    _SE[i] = cat([DEAD, DEAD, DEAD,
                  DEAD, c(i), e(i),
                  DEAD, s(i), se(i)])

NW = lambda h: _NW[h & 0777]
N  = lambda h:  _N[h & 0777]
NE = lambda h: _NE[h & 0777]

W  = lambda h:  _W[h & 0777]
C  = lambda h:     h & 0777
E  = lambda h:  _E[h & 0777]

SW = lambda h: _SW[h & 0777]
S  = lambda h:  _S[h & 0777]
SE = lambda h: _SE[h & 0777]

def cardinal(history, direction):
    transforms = {
        'NW': NW, 'N': N, 'NE': NE,
        'W':  W,  'C': C, 'E':  E,
        'SW': SW, 'S': S, 'SE': SE}
    return transforms[direction](history)

def opposite(history, direction):
    transforms = {
        'NW': SE, 'N': S, 'NE': SW,
        'W':  E,  'C': C, 'E':  W,
        'SW': NE, 'S': N, 'SE': NW}
    return transforms[direction](history)


class Historian(object):
    def __init__(self, rule):
        self.rule = rule
        self._mem = {}

    def Z(self, history):
        if self._mem.get(history) is not None:
            return self._mem[history]
        center = c(history)
        neighborcount = sum([nw(history), n(history), ne(history),
                             w(history),              e(history),
                             sw(history), s(history), se(history)])
        z = (center, neighborcount) in self.rule
        self._mem[history] = z
        return z

    def corroborate(self, history, report, direction):
        # Does a history jive with the report from the given direction?
        # A report is a history from a neighboring cell.
        return (cardinal(history, direction) ==
                opposite(report, direction))

    def check(self, history, **criteria):
        # Does the given history pass all the criteria?
        # Criteria are of the form NW=1, Z=0, nw=0
        transforms = {
            'NW': NW, 'N': N, 'NE': NE,
            'W':  W,  'C': C, 'E':  W,
            'SW': SW, 'S': S, 'SE': SE,
            'nw': nw, 'n': n, 'ne': ne,
            'w' : w,  'c': c, 'e' : e,
            'sw': sw, 's': s, 'se': se,
            'Z': self.Z,
            }
        
        for query, value in criteria.items():
            if query in transforms:
                if transforms[query](history) != value:
                    return False
        return True

    def was_alive(self, history):
        return c(history) == ALIVE
