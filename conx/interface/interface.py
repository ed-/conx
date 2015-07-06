#!/usr/bin/env python

from __future__ import print_function

import sys
import termios
import tty


# Utility display and input functions.
def getch():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch


def emit(s):
    print(s, end='')


def erase_screen():
    emit('%s[2J' % chr(27))


def move_cursor(row=None, column=None):
    ROW = 1 if row is None else row
    COLUMN = 1 if column is None else column
    SEMICOLON = ';' if ROW + COLUMN else ''
    emit('%s[%i%s%iH' % (chr(27), ROW, SEMICOLON, COLUMN))


class Interface(object):

    def __init__(self, automata, reverser_class):
        self.automata = automata
        self.reverser_class = reverser_class
        self.rows = self.automata.rows
        self.columns = self.automata.columns
        self.reverser = None
        self.guesses = {}
        self.status_line = ''
        self.cursor_row = 0
        self.cursor_column = 0

    def guess(self):
        if self.reverser is None:
            self.reverser = self.reverser_class(self.automata)

        for (row, column), state in self.guesses.items():
            self.reverser.narrow(row, column, c=state)

        try:
            for c in self.reverser.corroborate():
                self._draw_reverser(cloud=c)
                self.status_line = '\x1b[48;5;21mThinking...\x1b[0m'
                self._draw_status_line()
        except ZeroDivisionError:
            self.reverser = None
            self.status_line = '\x1b[48;5;196mImpossible!\x1b[0m'
            self._draw_status_line()
        else:
            self.status_line = ''

    def _draw_reverser(self, cloud=None):
        if self.reverser is None:
            return

        if cloud is None:
            cloud = self.reverser.cloud

        NORMAL = '\x1b[0m'

        ro, co = 2, 2
        def __draw_alibi(chance, length):
            if not length:
                return '\x1b[48;5;196m  '
            if chance == 1.0:
                return '\x1b[48;5;231m[]'
            if chance == 0.5:
                return '\x1b[48;5;22m<>'
            if chance == 0.0:
                return '\x1b[48;5;16m  '
            ansi_grey = 232 + int(round(chance * 23.0))
            return '\x1b[48;5;%im%2i' % (ansi_grey, min(length, 99))

        # Draw the reverser, if any, on the left.
        if self.reverser is not None:
            for r, row in enumerate(cloud):
                R = [__draw_alibi(*a) for a in row]
                move_cursor(ro + r, co)
                emit(''.join(R) + NORMAL)
            move_cursor(self.automata.rows + 3, 2)

    def _draw_automata(self):
        NORMAL = chr(27) + '[0m'
        tf = {
            0: '\x1b[48;5;16m  ',
            1: '\x1b[48;5;231m[]',
        }
        ro, co = 2, (2 * self.columns) + 6
        for row in range(self.automata.rows):
            R = [self.automata.cell_at(row, column)
                 for column in range(self.automata.columns)]
            R = [tf[cell] for cell in R]
            move_cursor(ro + row, co)
            emit(''.join(R) + NORMAL)

    def _draw_guesses(self):
        tf = {
            0: '\x1b[48;5;53m  \x1b[0m',
            1: '\x1b[48;5;53m[]\x1b[0m',
        }
        for (row, column), state in self.guesses.items():
            R, C = row + 2, (column * 2) + 2
            move_cursor(R, C)
            emit(tf[state])

    def _draw_cursor(self):
        face = '  '
        g = 0
        g = self.guesses.get((self.cursor_row, self.cursor_column))
        if g is None:
            if self.reverser is not None:
                alibi_here = self.reverser.alibi_at(self.cursor_row, self.cursor_column)
                face = '%2i' % min(99, len(alibi_here))
                g = self.reverser.alive_at(self.cursor_row, self.cursor_column)
        if g == 0.0:
            face = '  '
        if g == 0.5:
            face = '<>'
        if g == 1.0:
            face = '[]'
        move_cursor(self.cursor_row + 2, self.cursor_column * 2 + 2)
        emit('\x1b[48;5;18m%s\x1b[0m' % face)

    def _draw_status_line(self):
        if not self.status_line:
            return
        move_cursor(self.automata.rows + 3, 2)
        emit(self.status_line)
        
    def draw(self):
        erase_screen()
        self._draw_reverser()
        self._draw_guesses()
        self._draw_automata()
        self._draw_cursor()
        self._draw_status_line()
        move_cursor(self.automata.rows + 3, 2)

    def _cursor_up(self):
        self.cursor_row = max(0, self.cursor_row - 1)

    def _cursor_down(self):
        self.cursor_row = min(self.automata.rows - 1, self.cursor_row + 1)

    def _cursor_left(self):
        self.cursor_column = max(0, self.cursor_column - 1)

    def _cursor_right(self):
        self.cursor_column = min(self.automata.columns - 1, self.cursor_column + 1)

    def _cursor_dead(self):
        self.guesses[(self.cursor_row, self.cursor_column)] = 0

    def _cursor_alive(self):
        self.guesses[(self.cursor_row, self.cursor_column)] = 1

    def _cursor_clear(self):
        if (self.cursor_row, self.cursor_column) in self.guesses:
            del self.guesses[(self.cursor_row, self.cursor_column)]

    def run(self):
        while True:
            self.draw()
            C = None
            while C is None:
                C = getch()
            if C == 'n':
                self.automata.step()
            elif C == ' ':
                self.guess()
            elif C == 'q':
                break
            elif C == 'Q':
                break
            elif C == 'h':
                self._cursor_left()
            elif C == 'j':
                self._cursor_down()
            elif C == 'k':
                self._cursor_up()
            elif C == 'l':
                self._cursor_right()

            elif C == 'a':
                self._cursor_alive()
                self.guess()
            elif C == 's':
                self._cursor_clear()
                self.guess()
            elif C == 'd':
                self._cursor_dead()
                self.guess()
