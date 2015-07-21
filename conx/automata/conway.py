#!/usr/bin/env python

DEAD = 0
ALIVE = 1

class Conway(object):
    cells = None

    def __init__(self, cells):
        self.cells = cells[:]
        self.rule = [(0, 3), (1, 2), (1, 3)]

    def __str__(self):
        lookup = {
            DEAD:  '  ',
            ALIVE: '[]',
        }
        return '\n'.join([
            ''.join([
                lookup[cell]
                for cell in row])
            for row in self.cells])

    def __repr__(self):
        return '<Conway %ix%i>' % (self.rows, self.columns)

    @classmethod
    def load(cls, filename):
        text = ''
        cells = []
        with open(filename, 'r') as inf:
            text = inf.read()
        rows = text.split('\n')
        rows = [row for row in rows if not row.startswith('#')]
        rows = [[row[i:i+2] for i in range(0, len(row), 2)] for row in rows]
        lookup = {
            '  ': DEAD,
            '[]': ALIVE,
        }
        cells = [[lookup[cell] for cell in row] for row in rows]
        return cls(cells)

    @property
    def rows(self):
        return len(self.cells)

    @property
    def columns(self):
        if not self.cells:
            return 0
        return len(self.cells[0])

    def cell_at(self, row, column):
        # Negative indices are not meant to be relative.
        try:
            assert row >= 0
            assert column >= 0
            return self.cells[row][column]
        except (AssertionError, IndexError):
            # Any cell outside the board is DEAD.
            return DEAD

    def _rule(self, neighborhood):
        center = neighborhood[4]
        neighbors = sum(neighborhood) - center
        return ALIVE if (center, neighbors) in self.rule else DEAD

    def step(self):
        self.cells = [[self._rule(self.neighborhood(row, column))
                       for column in range(self.columns)]
                      for row in range(self.rows)]

    def neighborhood_coords(self, row, column):
        return [(row + r, column + c)
                for r in (-1, 0, 1)
                for c in (-1, 0, 1)]

    def neighborhood(self, row, column):
        return [self.cell_at(r, c)
                for (r, c) in self.neighborhood_coords(row, column)]

    def diff(self, other):
        size = self.rows * self.columns
        correct = sum([self.cell_at(row, column) == other.cell_at(row, column)
                       for row in range(self.rows) for column in range(self.columns)])
        return float(correct) / size


if __name__ == '__main__':
    import random
    coin = lambda p: p >= random.random()

    def randomdata(X):
        return [[coin(0.5) for c in range(X)]
                 for r in range(X)]

    Z = Conway(randomdata(25))
    x = ''
    while not x:
        Z.step()
        x = raw_input(Z)
