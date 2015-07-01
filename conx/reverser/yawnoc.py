#!/usr/bin/env python

import alibi

DEAD = 0
ALIVE = 1


class Yawnoc(object):

    def __init__(self, automata):
        self.detective = alibi.Detective(automata.rule)

        self.alibis = [[self.detective.narrow(range(512), Z=cell)
                        for cell in row]
                       for row in automata.cells]

        for row in range(self.rows):
            self.narrow(row, 0, nw=DEAD, w=DEAD, sw=DEAD)
            self.narrow(row, self.columns - 1, ne=DEAD, e=DEAD, se=DEAD)

        for column in range(self.columns):
            self.narrow(0, column, nw=DEAD, n=DEAD, ne=DEAD)
            self.narrow(self.rows - 1, column, sw=DEAD, s=DEAD, se=DEAD)

    def __str__(self):
        rows = []
        for row in self.alibis:
            r = ['%2i' % int(100 * self.detective.was_alive(c))
                 for c in row]
            rows.append(' '.join(r))
        return '\n'.join(rows)

    def __repr__(self):
        return '<Yawnoc %ix%i>' % (self.rows, self.columns)

    @property
    def rows(self):
        return len(self.alibis)

    @property
    def columns(self):
        if not self.alibis:
            return 0
        return len(self.alibis[0])

    @property
    def cloud(self):
        return [[(self.detective.was_alive(a), len(a))
                 for a in row]
                for row in self.alibis]

    def alibi_at(self, row, column):
        # Negative indices are not meant to be relative.
        try:
            assert row >= 0
            assert column >= 0
            return self.alibis[row][column]
        except (AssertionError, IndexError):
            return None

    def was_alive(self, alibi_obj):
        return self.detective.was_alive(alibi_obj)

    def neighborhood_coords(self, row, column):
        return [(row + r, column + c)
                for r in (-1, 0, 1)
                for c in (-1, 0, 1)]

    def neighborhood(self, row, column):
        return [self.alibi_at(r, c)
                for (r, c) in self.neighborhood_coords(row, column)]

    def alive_at(self, row, column):
        alibi_here = self.alibi_at(row, column)
        if alibi_here:
            return self.detective.was_alive(alibi_here)

    def narrow(self, row, column, **criteria):
        alibi_here = self.alibi_at(row, column)
        if alibi_here:
            alibi_here = self.detective.narrow(alibi_here, **criteria)
            self.alibis[row][column] = alibi_here

    def corroborate(self, remaining=None):
        if remaining is None:
            remaining = [(row, column)
                         for row in range(self.rows)
                         for column in range(self.columns)]
        while remaining:
            row, column = remaining.pop(0)
            alibi_here = self.alibi_at(row, column)
            if alibi_here is None:
                continue
            if not alibi_here:
                raise ZeroDivisionError()
            old_alibi_length = len(alibi_here)
            directions = ['NW', 'N', 'NE', 'W', None, 'E', 'SW', 'S', 'SE']
            for ((nrow, ncol), direction) in zip(self.neighborhood_coords(row, column),
                                                 directions):
                if direction is None:
                    continue
                neighbor = self.alibi_at(nrow, ncol)
                if neighbor is None:
                    continue
                alibi_here = self.detective.corroborate(alibi_here, neighbor, direction)
            if old_alibi_length > len(alibi_here):
                neighbors = [(row + dr, column + dc)
                             for dc in (-1, 0, 1)
                             for dr in (-1, 0, 1)]
                remaining.extend(neighbors)
                self.alibis[row][column] = alibi_here
                yield self.cloud

    def guess(self):
        remaining = [(row, column)
                     for row in range(self.rows)
                     for column in range(self.columns)]
        while remaining:
            row, column = remaining.pop(0)
            alibi_here = self.alibi_at(row, column)
            if alibi_here is None:
                continue
            old_alibi_length = len(alibi_here)
            was_alive = self.detective.was_alive(alibi_here)
            if was_alive < 0:
                continue
            if was_alive > 0.75:
                alibi_here = self.detective.narrow(alibi_here, c=ALIVE)
            elif was_alive <= 0.5:
                alibi_here = self.detective.narrow(alibi_here, c=DEAD)

            self.alibis[row][column] = alibi_here

            for b in self.corroborate([(row, column)]):
                yield self.cloud


if __name__ == '__main__':
    import argparse
    import random
    ap = argparse.ArgumentParser()
    ap.add_argument('-r', '--rows', type=int, default=16)
    ap.add_argument('-c', '--cols', type=int, default=16)
    ap.add_argument('-d', '--density', type=float, default=0.5)

    parsed = ap.parse_args()

    coin = lambda p: p >= random.random()

    def randomdata(rows, columns, density=0.5):
        return [[coin(density) for c in range(columns)]
                 for r in range(rows)]

    orig_cells = randomdata(parsed.rows, parsed.cols, parsed.density)

    Z = Yawnoc(orig_cells)

    for b in Z.corroborate():
        print b
        print
    print
