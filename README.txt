Conx: another attempt at reversing Conway's Game of Life

Detective-Conway was messy, and Yawnoc was too ambitious.
I took what I learned from either of those, and decided to leave the hardest part--
rolling back failed guesses--to humans. To do that, major improvements in the UI were
needed to facilitate this.

Figuring out the best way to keep (human) guesses from interfering with the yawnoc model was probably the most significant step here.

The basic usage is, ./main.py [size] will generate a random square board of size [size] and then walk it forward a single step to guarantee that it _can_ be reversed. From there, use hjkl to navigate the guess board (on the left). Space invokes the yawnoc engine to anneal the guess board, a/d marks a cell alive or dead, s removes that guess. If you get an inconsistent state, the board is wiped. Just hit Space or repeat the last mark to invoke the engine again. Lowercase q quits, and there's a handful of other things. < and > switch between boards, and n steps the goal board (on the right) foward once, so you can create your own goal boards, and then try to reverse them. Still working on loading, it's not quite working yet.

Conx makes excessive use of raw vt100 escapes to get colors and drive a primitive display. It looks best with a font that's about twice as tall as it is wide, and in a color terminal. I use iTerm2 in OS X and haven't gotten much of a chance to test it elsewhere for now.
