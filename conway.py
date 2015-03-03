#!/usr/bin/env python

import history

class Conway(object):
    cells = None

    def __init__(self, cells):
        self.cells = cells[:]

    def __str__(self):
        lookup = {
            history.DEAD:  '  ',
            history.ALIVE: '[]',
        }
        return '\n'.join([
            ''.join([
                lookup[cell]
                for cell in row])
            for row in self.cells])

    def __repr__(self):
        return '<Conway %ix%i>' % (self.rows, self.columns)

    @property
    def rows(self):
        return len(self.cells)

    @property
    def columns(self):
        if not self.cells:
            return 0
        return len(self.cells[0])

    def _cell_at(self, row, column):
        # Negative indices are not meant to be relative.
        try:
            assert row >= 0
            assert column >= 0
            return self.cells[row][column]
        except (AssertionError, IndexError):
            # Any cell outside the board is DEAD.
            return history.DEAD

    def step(self):
        self.cells = [[history.LIFE(self.neighborhood(row, column))
                       for column in range(self.columns)]
                      for row in range(self.rows)]

    def neighborhood_coords(self, row, column):
        return [(row + r, column + c)
                for r in (-1, 0, 1)
                for c in (-1, 0, 1)]

    def neighborhood(self, row, column):
        return [self._cell_at(r, c)
                for (r, c) in self.neighborhood_coords(row, column)]

    def diff(self, other):
        size = self.rows * self.columns
        correct = sum([self._cell_at(row, column) == other._cell_at(row, column)
                       for row in range(self.rows) for column in range(self.columns)])
        return float(correct) / size


if __name__ == '__main__':
    import random
    coin = lambda p: p >= random.random()

    def emptydata(X):
        return [[coin(0.5) for c in range(X)]
                 for r in range(X)]

    Z = Conway(emptydata(25))
    x = ''
    while not x:
        Z.step()
        x = raw_input(Z)
