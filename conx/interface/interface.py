#!/usr/bin/env python

from __future__ import print_function

import sys
import termios
import tty
from conx.common.guess import Guesses


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
    sys.stdout.flush()


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
        self.reverser = self.reverser_class(self.automata)
        self.status_line = ''
        self.cursor_row = 0
        self.cursor_column = 0
        self.show_guesses = False
        self.guesses = Guesses()

    def guess(self):
        self.status_line = '\x1b[48;5;21mThinking...\x1b[0m'
        self._draw_status_line()
        if self.reverser.impossible:
            self.reverser.reset()
            self._draw_reverser()

        for (row, column), state in self.guesses.as_dict().items():
            self.reverser.narrow(row, column, c=state)

        try:
            for ((r, c), chance, length) in self.reverser.corroborate():
                self._draw_one_guess((r, c), chance, length)
                self.status_line = '\x1b[48;5;21mThinking...\x1b[0m'
                self._draw_status_line()
        except ZeroDivisionError:
            self.status_line = '\x1b[48;5;196mImpossible!\x1b[0m'
            self._draw_status_line()
        else:
            self.status_line = ''
            self._draw_status_line()

    def _eval_and_draw(self):
        try:
            for ((r, c), chance, length) in self.reverser.evaluate_guesses(self.guesses):
                self._draw_one_guess((r, c), chance, length)
        except ZeroDivisionError:
            return False
        return True

    def autoguess(self):
        self.status_line = '\x1b[48;5;21mAutoguessing...\x1b[0m'
        self._draw_status_line()
        last_failure = None
        while True:
            ok = self._eval_and_draw()
            if ok:
                # Find the next unguessed spot.
                last_failure = None
                rc = self.reverser.next_guessable()
                if rc is None:
                    self.status_line = ''
                    self._draw_status_line()
                    return  # Nothing more to guess.
                # Guess that the next spot in the list was DEAD.
                self.guesses.append(rc, 0)

            else:
                # Failure. Remove the last guess from the list.
                last_failure = self.guesses.pop()
                if last_failure is None:
                    # Uh oh.
                    self.status_line = '\x1b[48;5;196mImpossible!\x1b[0m'
                    self._draw_status_line()
                    return
                rc, failed_guess = last_failure
                if failed_guess == 0:
                    # That spot wasn't DEAD. Try ALIVE.
                    self.guesses.append(rc, 1)
                else:
                    # It wasn't ALIVE either. Unwind.
                    while failed_guess == 1:
                        last_failure = self.guesses.pop()
                        rc, failed_guess = last_failure
                    self.guesses.append(rc, 1)
        self.status_line = ''
        self._draw_status_line()
        self._draw_reverser()

    def _draw_reverser(self):
        if self.reverser is None:
            return

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
            face = '%02i' % length if length < 100 else '  '
            return '\x1b[48;5;%im%s' % (ansi_grey, face)

        if self.reverser is not None:
            for r, row in enumerate(cloud):
                R = [__draw_alibi(*a) for a in row]
                move_cursor(ro + r, co)
                emit(''.join(R) + NORMAL)
            move_cursor(self.automata.rows + 3, 2)

    def _draw_one_guess(self, (row, column), chance, length):
        NORMAL = '\x1b[0m'

        ro, co = 2, 2
        cell = ''
        if not length:
            cell = '\x1b[48;5;196m  '
        elif chance == 1.0:
            cell = '\x1b[48;5;231m[]'
        elif chance == 0.5:
            cell = '\x1b[48;5;22m<>'
        elif chance == 0.0:
            cell = '\x1b[48;5;16m  '
        else:
            ansi_grey = 232 + int(round(chance * 23.0))
            face = '%02i' % length if length < 100 else '  '
            cell = '\x1b[48;5;%im%s' % (ansi_grey, face)

        move_cursor(ro + row, co + (column * 2))
        emit(cell + NORMAL)

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
        if not self.show_guesses:
            return
        tf = {
            0: '\x1b[48;5;53m  \x1b[0m',
            1: '\x1b[48;5;53m[]\x1b[0m',
        }
        for (row, column), state in self.guesses.as_dict().items():
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
        move_cursor(self.automata.rows + 3, 2)
        emit(' ' * self.automata.columns * 2)
        if not self.status_line:
            return
        move_cursor(self.automata.rows + 3, 2)
        emit(self.status_line)

    def draw(self):
        self._draw_reverser()
        self._draw_guesses()
        self._draw_automata()

        move_cursor((self.automata.rows / 2) + 2, self.automata.columns * 2 + 3)
        emit(">>")

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
        self.guesses.append((self.cursor_row, self.cursor_column), 0)
        self.guess()

    def _cursor_alive(self):
        self.guesses.append((self.cursor_row, self.cursor_column), 1)
        self.guess()

    def _undo_guess(self):
        rcv = self.guesses.pop()
        if rcv is not None:
            rc, v = rcv
            self.cursor_row, self.cursor_column = rc
        self._reguess()

    def _clear_guesses(self):
        self.guesses.reset()

    def _toggle_guesses(self):
        self.show_guesses = not self.show_guesses

    def _reguess(self):
        self.reverser.reset()
        self.guess()

    def _zap(self):
        rc = self.reverser.next_guessable()
        if rc is None:
            return
        self.cursor_row, self.cursor_column, = rc

    def save(self, problem='original.gol', solution='solution.gol'):
        with open(problem, "w") as outf:
            outf.write("%s\n" % self.automata)
        with open(solution, "w") as outf:
            S = self.automata.__class__(self.reverser.bestguess())
            outf.write("%s\n" % S)

    def run(self):
        erase_screen()
        self.draw()
        self.guess()
        while True:
            try:
                self.draw()
                C = None
                while C is None:
                    C = ord(getch())
                if C in [3, 17]:
                    # Ctrl-c or Ctrl-q to quit.
                    break
                if C == 27:
                    # Arrow keys to move.
                    if getch() != '[':
                        continue
                    arrow = getch()
                    if arrow == 'A':
                        self._cursor_up()
                    elif arrow == 'D':
                        self._cursor_left()
                    elif arrow == 'B':
                        self._cursor_down()
                    elif arrow == 'C':
                        self._cursor_right()

                C = chr(C)
                if C == 'a':
                    self._cursor_alive()
                elif C == 'd':
                    self._cursor_dead()
                elif C == 'u':
                    self._undo_guess()

                elif C == 'g':
                    self._toggle_guesses()

                elif C == '!':
                    self.autoguess()
                elif C == ';':
                    self._zap()

                elif C == 'S':
                    self.save()
            except KeyboardInterrupt:
                erase_screen()
                move_cursor(1, 1)
                break

    def autorun(self):
        try:
            erase_screen()
            self.guess()
            self.autoguess()
            erase_screen()
            self._draw_reverser()
            self._draw_automata()
            move_cursor((self.automata.rows / 2) + 2, self.automata.columns * 2 + 3)
            emit(">>")
            move_cursor(self.automata.rows + 3, 2)
            self.save()
        except KeyboardInterrupt:
            erase_screen()
            move_cursor(1, 1)
