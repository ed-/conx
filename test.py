#!/usr/bin/env python
from conx.automata import conway

import argparse
ap = argparse.ArgumentParser()
ap.add_argument('before', type=str)
ap.add_argument('after', type=str)
args = ap.parse_args()
B = conway.Conway.load(args.before)
B.step()
A = conway.Conway.load(args.after)
if A.diff(B) == 1.0:
    print "CORRECT!", A.diff(B)
else:
    print "FAILURE.", A.diff(B)
