#!/usr/bin/env python

import history
from colorize import GRAYize

# Alibi functions.

def long_format(alibi, prefix=''):
    O = ['......', '....[]', '..[]..', '..[][]', '[]....', '[]..[]', '[][]..', '[][][]']
    pfx = (prefix + (' ' * 10))[:10] + ':'
    ppfx = ' ' * len(pfx)
    topline = ppfx + ' / '  + ' '.join([O[(h & 0o700) >> 6] for h in alibi]) + ' \\'
    midline =  pfx + ' | '  + ' '.join([O[(h & 0o70)  >> 3] for h in alibi]) + ' |'
    botline = ppfx + ' \\ ' + ' '.join([O[ h &  0o7       ] for h in alibi]) + ' /'
    return '\n'.join([topline, midline, botline]) + '\n'

def colored_format(alibi):
    alive = was_alive(alibi)
    '''
    face = '%2i' % len(alibi)
    if alive == 1.0:
        face = '()'
    if alive == 0.0:
        face = '..'
    if len(alibi) > 99:
        face = '99'
    '''
    face = '  '
    if alive == 0.5:
        face = '--'
    return GRAYize(face, alive)

def corroborate(alibi, testimony, direction):
    # Eliminate from an alibi all histories that aren't backed up by
    # any of the reports in the testimony. A testimony is an alibi
    # from a neighboring cell.
    #adjusted_ts = set([opposite(h, direction) for h in testimony])
    adjusted_ts = [history.opposite(h, direction) for h in testimony]
    adjusted_hs = [history.cardinal(h, direction) for h in alibi]
    return [h for h in alibi if history.cardinal(h, direction) in adjusted_ts]

def narrow(alibi, **criteria):
    # Eliminate from an alibi all histories that don't meet all of
    # the criteria. Criteria are of the form NW=1, Z=0, nw=0
    return [h for h in alibi if history.check(h, **criteria)]

def was_alive(alibi):
    # Figure out what fraction of an alibi's histories claim c was ALIVE.
    live_histories = sum([history.was_alive(h) for h in alibi])
    return float(live_histories) / len(alibi)
