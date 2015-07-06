#!/usr/bin/env python

import argparse
import random

from interface import interface
from automata import conway
from reverser import yawnoc

coin = lambda p: p >= random.random()

def randomdata(X):
    return [[coin(0.5) for c in range(X)]
             for r in range(X)]

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('size', type=int, default=10)
    args = ap.parse_args()
    C = conway.Conway(randomdata(args.size))
    C.step()

    I = interface.Interface(C, yawnoc.Yawnoc)
    I.run()
