#!/usr/bin/env python

ESC = chr(27) + '['
NORMAL = ESC + "0m"


def ANSI(A):
    return ESC + ('48;5;%im' % A)


def GRAY(V):
    return ANSI(232 + int(round(V * 23.0)))


def RGB(R, G, B):
    return ANSI(16 + (36 * R) + (6 * G) + B)


def RGBize(text, rgb):
    return "%s%s%s" % (RGB(*rgb), text, NORMAL)


def ANSIize(text, ansi):
    return "%s%s%s" % (ANSI(ansi), text, NORMAL)


def GRAYize(text, gray):
    return "%s%s%s" % (GRAY(gray), text, NORMAL)
