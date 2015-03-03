#!/usr/bin/env python
# ANSI/VT100 Terminal Control Escape Sequences
# http://www.termsys.demon.co.uk/vtansi.htm
# Transliterated by Ed Cranford

from __future__ import print_function

# Many computer terminals and terminal emulators support colour and cursor control through a system of escape sequences. One such standard is commonly referred to as ANSI Colour. Several terminal specifications are based on the ANSI colour standard, including VT100.

# %(ESC)s represents the ASCII "escape" character, 0x1B. Bracketed tags represent modifiable decimal parameters; eg. {ROW} would be replaced by a row number.
ESC = chr(27)

def emit(s):
    print(s, end='')

def reset_device():
    # Reset all terminal settings to default.
    emit('%sbc' % ESC)

def enable_line_wrap():
    emit('%s[7h' % ESC)
    # Text wraps to next line if longer than the length of the display area.

def disable_line_wrap():
    # Disables line wrapping.
    emit('%s[7l' % ESC)

def font_set_g0():
    # Set default font.
    emit('%s(' % ESC)

def font_set_g1():
    # Set alternate font.
    emit('%s)' % ESC)

def cursor_home(row=None, column=None):
    # Sets the cursor position where subsequent text will begin. If no row/column parameters are provided (ie. %(ESC)s[H), the cursor will move to the home position, at the upper left of the screen.
    ROW = 1 if row is None else row
    COLUMN = 1 if column is None else column
    SEMICOLON = ';' if ROW + COLUMN else ''
    emit('%s[%i%s%iH' % (ESC, ROW, SEMICOLON, COLUMN))

def cursor_up(count=1):
    # Moves the cursor up by COUNT rows; the default count is 1.
    emit('%s[%iA' % (ESC, count))

def cursor_down(count=1):
    # Moves the cursor down by COUNT rows; the default count is 1.
    emit('%s[%iB' % (ESC, count))

def cursor_forward(count=1):
    # Moves the cursor forward by COUNT columns; the default count is 1.
    emit('%s[%iC' % (ESC, count))

def cursor_backward(count=1):
    # Moves the cursor backward by COUNT columns; the default count is 1.
    emit('%s[%iD' % (ESC, count))

def force_cursor_position(row=None, column=None):
    # Identical to Cursor Home.
    cursor_home(row, column)

def save_cursor():
    # Save current cursor position.
    emit('%s[s' % ESC)

def restore_cursor():
    # Restores cursor position after a Save Cursor.
    emit('%s[u' % ESC)

def save_cursor_and_attrs():
    # Save current cursor position.
    emit('%s7' % ESC)

def restore_cursor_and_attrs():
    # Restores cursor position after a Save Cursor.
    emit('%s8' % ESC)

def scroll_screen():
    # Enable scrolling for entire display.
    emit('%s[r' % ESC)

def scroll_screen(start=None, end=None):
    # Enable scrolling from row {start} to row {end}.
    START = '' if start is None else start
    END = '' if end is None else end
    SEMICOLON = ';' if START + END else ''
    emit('%s[%i%s%sr' % (ESC, START, SEMICOLON, END))

def scroll_down():
    # Scroll display down one line.
    emit('%sD' % ESC)

def scroll_up():
    # Scroll display up one line.
    emit('%sM' % ESC)

def set_tab():
    # Sets a tab at the current position.
    emit('%sH' % ESC)

def clear_tab():
    # Clears tab at the current position.
    emit('%s[g' % ESC)

def clear_all_tabs():
    # Clears all tabs.
    emit('%s[3g' % ESC)

def erase_end_of_line():
    # Erases from the current cursor position to the end of the current line.
    emit('%s[K' % ESC)

def erase_start_of_line():
    # Erases from the current cursor position to the start of the current line.
    emit('%s[1K' % ESC)

def erase_line():
    # Erases the entire current line.
    emit('%s[2K' % ESC)

def erase_down():
    # Erases the screen from the current line down to the bottom of the screen.
    emit('%s[J' % ESC)

def erase_up():
    # Erases the screen from the current line up to the top of the screen.
    emit('%s[1J' % ESC)

def erase_screen():
    # Erases the screen with the background colour and moves the cursor to home.
    emit('%s[2J' % ESC)

def set_key_definition(keycode, text):
    # Associates a string of text to a keyboard key. {key} indicates the key by its ASCII value in decimal.
    KEY = '' if keycode is None else keycode
    TEXT = '' if text is None else text
    emit('%s[%s;"%s"p' % (ESC, KEY, TEXT))

def web_hex_to_ansi_color(webhex):
    r, g, b = 0, 0, 0
    if webhex.startswith('#'):
        if len(webhex) == 4:  # #RGB shorthand
            r, g, b = webhex[1], webhex[2], webhex[3]
            r, g, b = int(r, 16) * 17, int(g, 16) * 17, int(b, 16) * 17
        elif len(webhex) == 7: # #RRGGBB
            r, g, b = webhex[1:3], webhex[3:5], webhex[5:7]
            r, g, b = int(r, 16), int(g, 16), int(b, 16)
        else:
            raise ValueError("Use #RGB or #RRGGBB form.")
    else:
        raise ValueError("Use #RGB or #RRGGBB form.")
    r, g, b = tuple(int(round(x / 51.0)) for x in (r, g, b))
    return (16 + (36 * r) + (6 * g) + b)

def set_text_color(fg=None, bg=None):
    if bg is not None:
        emit('%s[48;5;%im' % (ESC, web_hex_to_ansi_color(bg)))
    if fg is not None:
        emit('%s[38;5;%im' % (ESC, web_hex_to_ansi_color(fg)))

def reset_text_color():
    emit('%s[0m' % ESC)

def draw_box(toprow=1, leftcolumn=1, rows=0, columns=0, chars='+-+| |+-+'):
    # chars is of the form 'ABCD FGHI':
    # ABC
    # D F
    # GHI
    A, B, C, D, _, F, G, H, I = tuple(chars)
    if rows == 0 or columns == 0:
        return
    header = [B] * columns
    header[0] = A
    header[-1] = C
    header = ''.join(header)
    footer = [H] * columns
    footer[0] = G
    footer[-1] = I
    footer = ''.join(footer)
        
    save_cursor()
    cursor_home(toprow, leftcolumn)
    emit(header)
    for row in range(rows-2):
        cursor_home(toprow + row + 1, leftcolumn)
        emit(D)
        cursor_home(toprow + row + 1, leftcolumn + columns - 1)
        emit(F)
    cursor_home(toprow + rows - 1, leftcolumn)
    emit(footer)
    restore_cursor()

if __name__ == '__main__':
    erase_screen()
    set_text_color('#ff0000')
    draw_box(1, 1, 25, 80, '+=+| |+-+')
    reset_text_color()
    force_cursor_position(row=2, column=2)
