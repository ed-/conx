Conx: another attempt at reversing Conway's Game of Life

Detective-Conway was messy, and Yawnoc was too ambitious.
I took what I learned from either of those, and decided to leave the hardest part--
rolling back failed guesses--to humans. To do that, major improvements in the UI were
needed to facilitate this.

Figuring out the best way to keep (human) guesses from interfering with the yawnoc model was probably the most significant step here.

Usage:
    ./main.py --size [size]

    to generate a random size x size board, or

    ./main.py --load [filename]

    to load a .gol file, of which several hundred samples have been included in the samples directory.

Controls:
    h j k l - move the cursor around the left board. H and L are left and right, J and K are down and up.
    a       - marks the cell under the cursor as "previously alive", and then squares your guess against the board. if the board is blanked and you see the message "Impossible!", just clear or reverse your guess and try again.
    d       - marks the cell as "previously dead", and proceeds just like with 'a'.
    s       - clears a guess under the cell.
    space   - runs the guessing engine with the current work. use it when you first load a state, or after you clear a wrong guess.
    q or Q  - quits. doesn't work while the engine is running.
    n       - steps the right-side board forward once using Conway rules.

Conx makes excessive use of raw vt100 escapes to get colors and drive a primitive display. It looks best with a font that's about twice as tall as it is wide, and in a color terminal. I use iTerm2 in OS X and haven't gotten much of a chance to test it elsewhere for now.
