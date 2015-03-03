#!/usr/bin/env python

#TODO: integrate Yawnoc's brains to get the closest possible guess
#TODO: color
#TODO: double cursors, track row/column on edges

import random

import conway
import yawnoc
import inkey
import vt100
import colorize

BLUE = lambda t: colorize.RGBize(t, (0, 0, 5))
RED = lambda t: colorize.RGBize(t, (5, 0, 0))
PURPLE = lambda t: colorize.RGBize(t, (2, 0, 2))
BLACK = lambda t: colorize.RGBize(t, (0, 0, 0))
WHITE = lambda t: colorize.RGBize(t, (5, 5, 5))

coin = lambda p: p >= random.random()

cycle = lambda g: {None: 0, 0: 1, 1: None}.get(g)
toggle = lambda g: {0: 1, 1: 0}.get(g, 0)

def randomdata(size, density):
    return [[coin(density) for c in range(size)]
             for r in range(size)]

def emptydata(size):
    return [[0 for c in range(size)]
             for r in range(size)]


class Conx(object):
    size = 0

    _goal = None
    _guesses = None
    _yawnoc = None

    _cbd = 0
    _crow = 0
    _ccol = 0

    def __init__(self, size=20, density=0.5):
        self.size = max(size, 3)
        self._goal = conway.Conway(randomdata(self.size, density))
        self._goal.step()
        self._guesses = {}
        self._yawnoc = None

    def move_left(self):
        self._ccol -= 1
        if self._ccol < 0:
            self._ccol = 0

    def move_right(self):
        self._ccol += 1
        if self._ccol > (self.size - 1):
            self._ccol = (self.size - 1)

    def move_up(self):
        self._crow -= 1
        if self._crow < 0:
            self._crow = 0

    def move_down(self):
        self._crow += 1
        if self._crow > (self.size - 1):
            self._crow = (self.size - 1)

    def cycle(self):
        if self._cbd == 0:
            g = self._guesses.get((self._crow, self._ccol))
            g = {None: 0, 0: 1, 1: None}[g]
            if g is None:
                del self._guesses[(self._crow, self._ccol)]
            else:
                self._guesses[(self._crow, self._ccol)] = g
        else:
            self._goal.cells[self._crow][self._ccol] = toggle(
                self._goal.cells[self._crow][self._ccol])

    def swapboards(self, side=None):
        if side == '<':
            self._cbd = 0
        elif side == '>':
            self._cbd = 1
        else:
            self._cbd = 1 - self._cbd

    def clearboard(self):
        if self._cbd == 0:
            self._guesses = {}
        else:
            self._goal = conway.Conway(emptydata(self.size))
        self._yawnoc = None

    def randomize(self):
        self._goal = conway.Conway(randomdata(self.size, 0.5))
        self._goal.step()
        self._yawnoc = None

    def step(self):
        self._goal.step()

    def guess(self):
        if self._yawnoc is None:
            self._yawnoc = yawnoc.Yawnoc(self._goal.cells)
            
        for (row, column), state in self._guesses.items():
            alibi_here = self._yawnoc.narrow(row, column, c=state)
        vt100.cursor_home(self.size + 3, 0)
        vt100.emit(BLUE("Thinking..."))
        try:
            for b in self._yawnoc.corroborate():
                for row, line in enumerate(b.split('\n')):
                    vt100.cursor_home(row + 2, 2)
                    print line
        except ZeroDivisionError:
            self._yawnoc = None
            vt100.cursor_home(self.size + 3, 0)
            vt100.emit(RED("Impossible!"))

    def run(self):
        while True:
            self.draw()
            C = None
            while C is None:
                C = inkey.getch()
            if C == 'f':
                self.cycle()
            elif C == ' ':
                self.cycle()
            elif C == '<':
                self.swapboards('<')
            elif C == '>':
                self.swapboards('>')
            elif C == 'j':
                self.move_down()
            elif C == 'k':
                self.move_up()
            elif C == 'h':
                self.move_left()
            elif C == 'l':
                self.move_right()
            elif C == 'Q':
                break
            elif C == 'C':
                self.clearboard()
            elif C == 'R':
                self.randomize()
            elif C == 'S':
                self.step()
            elif C == 'G':
                self.guess()

    def draw(self):
        vt100.erase_screen() 

        # Draw the Yawnoc underneath
        if self._yawnoc is not None:
            ystring = str(self._yawnoc)
            for row, yline in enumerate(ystring.split('\n')):
                vt100.cursor_home(row + 2, 2)
                print yline

        cstring = {0: PURPLE('  '), 1: PURPLE('[]')}
        # Draw the guesses
        for (row, column), state in self._guesses.items():
            R, C = row + 2, (column * 2) + 2
            guesscell = cstring[state]
            vt100.cursor_home(R, C)
            vt100.emit(guesscell)
            
        # Generate the result of the guesses
        # Compare guess.step to goal and highlight the problems

        # Find the cells in goal that are wrong
        wrong = []

        cstring = {0: BLACK('  '), 1: WHITE('[]')}
        # Draw the goal board
        for row in range(self.size):
            for column in range(self.size):
                goalcell = self._goal._cell_at(row, column)
                R, C = row + 2, (column * 2) + (2 * self.size) + 4
                vt100.cursor_home(R, C)
                goalcell = cstring[goalcell]
                if (row, column) in wrong:
                    goalcell = RED(goalcell)
                vt100.emit(goalcell)

        # Draw the cursor
        crow, ccol = (self._crow) + 2, (self._ccol * 2) + 2 + ((2 + (2 * self.size)) * self._cbd)
        cstring = {0: BLUE('  '), 1: BLUE('[]')}
        curtext = self._guesses.get((self._crow, self._ccol), 0)
        if self._cbd == 1:
            curtext = self._goal._cell_at(self._crow, self._ccol)
            
        vt100.cursor_home(crow, ccol)
        vt100.emit(cstring[curtext])

        # Draw the stats
        if self._yawnoc is not None:
            # Print the alibi at the cursor
            vt100.cursor_home(self.size + 3, 0)
            #vt100.emit("Correct: %3i/400 (%3.3f%%)" % (correct, correct / 4.0))
        vt100.cursor_home(self.size + 4, 0)


def main(size):
    game = Conx(size)
    game.run()


if __name__ == '__main__':
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument('size', type=int)
    parsed = ap.parse_args()
    main(size=parsed.size)
