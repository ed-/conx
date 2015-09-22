#!/usr/bin/env python

import argparse
import random

from conx.interface import interface
from conx.automata import conway
from conx.reverser import yawnoc

coin = lambda p: p >= random.random()

def randomdata(X):
    return [[coin(0.333) for c in range(X)]
             for r in range(X)]

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--size', type=int, default=10)
    ap.add_argument('--load', type=str)
    args = ap.parse_args()
    C = None
    if args.load:
        C = conway.Conway.load(args.load)
    else:
        C = conway.Conway(randomdata(args.size))
        C.step()

    I = interface.Interface(C, yawnoc.Yawnoc)
    I.run()
    with open("GOAL", "w") as outf:
        outf.write("%s" % C)
    with open("GUESS", "w") as outf:
        G = conway.Conway(I.reverser.bestguess())
        outf.write("%s" % G)
