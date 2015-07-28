#!/usr/bin/env python

import history

# Alibi functions.

class Detective(object):
    def __init__(self, rule):
        self.historian = history.Historian(rule)

    def narrow(self, alibi, **criteria):
        # Eliminate from an alibi all histories that don't meet all of
        # the criteria. Criteria are of the form NW=1, Z=0, nw=0
        return [h for h in alibi if self.historian.check(h, **criteria)]

    def corroborate(self, alibi, testimony, direction):
        # Eliminate from an alibi all histories that aren't backed up by
        # any of the reports in the testimony. A testimony is an alibi
        # from a neighboring cell.
        if not alibi:
            return alibi
        if not testimony:
            return alibi
        adjusted_ts = [history.opposite(h, direction) for h in testimony]
        return [h for h in alibi if history.cardinal(h, direction) in adjusted_ts]

    def was_alive(self, alibi):
        # Figure out what fraction of an alibi's histories claim c was ALIVE.
        if not alibi:
            return -1
        live_histories = sum([self.historian.was_alive(h) for h in alibi])
        return float(live_histories) / len(alibi)
