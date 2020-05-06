class Guesses(object):
    def __init__(self):
        self._items = []

    def as_dict(self):
        D = {}
        for (k, v) in self._items:
            if v is None:
                if k in D:
                    del D[k]
            else:
                D[k] = v
        return D

    def __str__(self):
        return ', '.join(["(%i, %i): %i" % (r, c, v) for ((r, c), v) in self._items])

    def __bool__(self):
        return bool(self._items)

    def __in__(self, needle):
        return needle in self.as_dict()

    def __len__(self):
        return len(self._items)

    def get(self, key, default=None):
        D = self.as_dict()
        return D.get(key, default)

    def append(self, k, v):
        self._items.append((k, v))

    def pop(self):
        if self._items:
            return self._items.pop()
