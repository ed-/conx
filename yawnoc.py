#!/usr/bin/env python

import alibi
import conway
from history import ALIVE
from history import DEAD


class Yawnoc(conway.Conway):
    # A special Conway that doesn't step forward, but tries to step backward.
    def __init__(self, cells):
        self.cells = [[alibi.narrow(range(512), LIFE=cell)
                       for cell in row]
                      for row in cells]

        for row in range(self.rows):
            #edge = self.columns - 1
            self.narrow(row, 0, nw=DEAD, w=DEAD, sw=DEAD)
            #self.cells[row][0] = alibi.narrow(self.cells[row][0],
            #                                  nw=DEAD, w=DEAD, sw=DEAD)
            self.narrow(row, self.columns - 1, ne=DEAD, e=DEAD, se=DEAD)
            #self.cells[row][edge] = alibi.narrow(self.cells[row][edge],
            #                                     ne=DEAD, e=DEAD, se=DEAD)

        for column in range(self.columns):
            #edge = self.rows - 1
            self.narrow(0, column, nw=DEAD, n=DEAD, ne=DEAD)
            #self.cells[0][column] = alibi.narrow(self.cells[0][column],
            #                                     nw=DEAD, n=DEAD, ne=DEAD)
            self.narrow(self.rows - 1, column, sw=DEAD, s=DEAD, se=DEAD)
            #self.cells[edge][column] = alibi.narrow(self.cells[edge][column],
            #                                        sw=DEAD, s=DEAD, se=DEAD)

    def __str__(self):
        return '\n'.join([
            ''.join([
                alibi.colored_format(cell) for cell in row])
            for row in self.cells])

    def __repr__(self):
        return '<Yawnoc %ix%i>' % (self.rows, self.columns)

    def _cell_at(self, row, column):
        # Negative indices are not meant to be relative.
        try:
            assert row >= 0
            assert column >= 0
            return self.cells[row][column]
        except (AssertionError, IndexError):
            return None

    def alive_at(self, row, column):
        alibi_here = self._cell_at(row, column)
        if alibi_here:
            return alibi.was_alive(alibi_here)

    def step(self):
        # Yawnoc does not step forward.
        pass

    def undo(self):
        # Yawnoc does not have an undo.
        pass

    def narrow(self, row, column, **criteria):
        alibi_here = self._cell_at(row, column)
        if alibi_here:
            alibi_here = alibi.narrow(alibi_here, **criteria)
            self.cells[row][column] = alibi_here

    def corroborate(self, remaining=None):
        if remaining is None:
            remaining = [(row, column)
                         for row in range(self.rows)
                         for column in range(self.columns)]
        while remaining:
            row, column = remaining.pop(0)
            alibi_here = self._cell_at(row, column)
            if alibi_here is None:
                continue
            if not alibi_here:
                continue
            old_alibi_length = len(alibi_here)
            directions = ['NW', 'N', 'NE', 'W', None, 'E', 'SW', 'S', 'SE']
            for ((nrow, ncol), direction) in zip(self.neighborhood_coords(row, column),
                                                 directions):
                if direction is None:
                    continue
                neighbor = self._cell_at(nrow, ncol)
                if neighbor is None:
                    continue
                alibi_here = alibi.corroborate(alibi_here, neighbor, direction)
            if old_alibi_length > len(alibi_here):
                neighbors = [(row + dr, column + dc)
                             for dc in (-1, 0, 1)
                             for dr in (-1, 0, 1)]
                remaining.extend(neighbors)
                self.cells[row][column] = alibi_here
                yield str(self)

    def guess(self):
        remaining = [(row, column)
                     for row in range(self.rows)
                     for column in range(self.columns)]
        while remaining:
            row, column = remaining.pop(0)
            alibi_here = self._cell_at(row, column)
            if alibi_here is None:
                continue
            old_alibi_length = len(alibi_here)
            was_alive = alibi.was_alive(alibi_here)
            if was_alive > 0.75:
                alibi_here = alibi.narrow(alibi_here, c=ALIVE)
            elif was_alive <= 0.5:
                alibi_here = alibi.narrow(alibi_here, c=DEAD)

            self.cells[row][column] = alibi_here

            for b in self.corroborate([(row, column)]):
                yield str(self)

    def bestguess(self, provided=None):
        # Provided is a dictionary of type {(row, column): ALIVE|DEAD}
        if provided is None:
            provided = {}
        oldcells = self.cells[:]
        for (row, column), state in provided.items():
            alibi_here = self._cell_at(row, column)
            alibi_here = alibi.narrow(alibi_here, c=state)
            self.cells[row][column] = alibi_here
        self.corroborate()

        live_filter = lambda x: ALIVE if x >= 0.75 else DEAD
        cells = [[live_filter(alibi.was_alive(a)) for a in row]
                 for row in self.cells]
        self.cells = oldcells[:]
        return conway.Conway(cells)


if __name__ == '__main__':
    import argparse
    import random
    import vt100

    random.seed("PETERSELLERS")
    ap = argparse.ArgumentParser()
    ap.add_argument('-r', '--rows', type=int, default=16)
    ap.add_argument('-c', '--cols', type=int, default=16)
    ap.add_argument('-d', '--density', type=float, default=0.5)

    parsed = ap.parse_args()

    coin = lambda p: p >= random.random()

    def randomdata(rows, columns, density=0.5):
        return [[coin(density) for c in range(columns)]
                 for r in range(rows)]

    import conway
    orig_cells = randomdata(parsed.rows, parsed.cols, parsed.density)

    C = conway.Conway(orig_cells)
    C.step()
    print C
    print

    Z = Yawnoc(C.cells)

    vt100.erase_screen()
    vt100.cursor_home()

    for b in Z.corroborate():
        vt100.cursor_home()
        print b
    print

    for b in Z.guess():
        vt100.cursor_home()
        print b
    print

    G = Z.bestguess()
    print "Guess:"
    print G
    print

    print "Original:"
    print conway.Conway(orig_cells)
    print

    print "Next of guess:"
    G.step()
    print G
    print

    print "Goal:"
    print C
    print

    print "Accuracy: %0.3f" % (100.0 * C.diff(G))
