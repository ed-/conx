#!/usr/bin/env python

import argparse
import random

from conx.interface import interface
from conx.automata import conway
from conx.reverser import yawnoc

coin = lambda p: p >= random.random()

def randomdata_(X):
    return [[coin(0.333) for c in range(X)]
             for r in range(X)]

def randomdata(X):
    return [[coin(0.5) for c in range(X)]
             for r in range(X)]

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--size', type=int, default=10)
    ap.add_argument('--load', type=str)
    ap.add_argument('--auto', dest='auto', action='store_true')
    args = ap.parse_args()
    C = None
    if args.load:
        C = conway.Conway.load(args.load)
    else:
        C = conway.Conway(randomdata(args.size))
        for i in range(12):
          C.step()

    I = interface.Interface(C, yawnoc.Yawnoc)
    if args.auto:
        I.autorun()
    else:
        I.run()
