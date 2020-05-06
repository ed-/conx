Conx: Conway's Game of Life reversal tool.

Generate or load a grid of automata, and this tool can generate a grid whose next state is the one you gave it.

Usage:
    ./main.py --size [size] [--auto]

    to generate a random size x size board, or

    ./main.py --load [filename] [--auto]

    to load a .gol file, described below.

    The --auto option jumps right to the autosolving part, forgoing human input.


Controls:
    arrow keys - move the cursor around the left board.
    a       - marks the cell under the cursor as "previously alive", and then squares your guess against the board. if the board is blanked and you see the message "Impossible!", just undo your last guess and try again.
    d       - marks the cell as "previously dead", and proceeds just like with 'a'.
    u       - undo the last guess marked.
    ctrl-c or ctrl-q - quits.
    !       - invoke the autoguesser. if your board can be solved, this will generate a solution given enough time.
    ;       - zap to next "interesting" cell. this is the cell with the most ambiguous history.
    S       - save the current guess and goal boards as solution.gol and original.gol respectively.

Conx makes excessive use of raw vt100 escapes to get colors and drive a primitive display. It looks best with a font that's about twice as tall as it is wide, and in a color terminal. I use iTerm2 in OS X and haven't gotten much of a chance to test it elsewhere for now.


GOL files
    A simple text file, using just two symbols to represent a rectangular grid.
    '[]' is a live cell, and '  ' is a dead cell. Any short rows will be assumed to be dead.
    Lines starting with '#' are ignored.
