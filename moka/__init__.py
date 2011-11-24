import operator as op


class Blank:
    pass

_ = Blank


class List(list):
    """
    List is a wrapper around the builtin list.
    It provides a chainable interface and enhances it with
    these methods:

    do
    tee
    map
    keep
    rem
    some/has
    all
    count
    find
    empty
    attr
    item
    invoke

    Todo:
    reduce/fold
    """

    @staticmethod
    def _proxy(method_name):
        """
        Make builtin list methods return self instead of None.
        """
        def wrap(self, *args, **kwargs):
            inst = List(self)
            getattr(list, method_name)(inst, *args, **kwargs)
            return inst

        setattr(List, method_name, wrap)

    def _moka_assign(self, items):
        """
        Assign enumerable to the list and return
        self instead of None
        """
        self[:] = items
        return self

    def _f(self, f, *args, **kwargs):
        """
        Parse arguments and return a new function.

        If there's no argument, return a function that call f.
        If there are arguments, use the partial syntax and bind
          the parameters to f.
        """
        if not args and not kwargs:
            return lambda x: f(x)

        if Blank not in args:
            return lambda x: f(x, *args, **kwargs)

        args = list(args)
        pos = args.index(Blank)

        def tmp(x):
            args[pos] = x
            return f(*args, **kwargs)
        return tmp

    def clone(self):
        """
        Returns a copy of the List
        """
        return List(self)

    def tee(self, *args, **kwargs):
        """
        Like 'do', but return self instead of the result.
        """
        self.last_value = self._f(*args, **kwargs)(self)
        return self

    def do(self, *args, **kwargs):
        """
        Call a method and pass 'self' as first parameter.
        List(..).do(some_method) <=> some_method(List(...))
        """
        return self._f(*args, **kwargs)(self)

    def map(self, *args, **kwargs):
        """
        List([1,2]).map(fn) <=> map(fn, [1,2])
        """
        f = self._f(*args, **kwargs)
        return self._moka_assign(f(x) for x in self)

    def invoke(self, name, *args, **kwargs):
        """
        List([1,2]).invoke('__str__')
        <=>
        List([1,2]).map(lambda x: x.__str__())
        """
        return self.map(lambda x: getattr(x, name)(*args, **kwargs))

    def attr(self, attr):
        """
        List([obj]).attr('attr')
        <=>
        List([obj]).map(lambda x: x.attr)
        """
        return self.map(lambda x: getattr(x, attr))

    def item(self, item):
        """
        List([obj]).item('item')
        <=>
        List([obj]).map(lambda x: x[item])
        """
        return self.map(lambda x: x[item])

    def empty(self, *args, **kwargs):
        """
        Returns True if the list is empty.
        A predicate can be given to specify 'what is True'.
        List(..).empty(lambda x: x == None)
        """
        if not args and not kwargs:
            return not bool(self)
        else:
            f = self._f(*args, **kwargs)

            for x in self:
                if f(x):
                    continue
                return False
            return True

    def count(self, *args, **kwargs):
        """
        Returns the number of elements.
        Can take a function to specify 'what to count'.
        List(..).count(lambda x: x > 0)
        """
        if not args and not kwargs:
            return len(self)
        else:
            return (self
                     .clone()
                     .keep(*args, **kwargs)
                     .count())

    def find(self, *args, **kwargs):
        """
        Return the first element that matches 'predicate'
        or returns None.
        List(..).find(lambda x: x == 3)
        """
        f = self._f(*args, **kwargs)

        for x in self:
            if f(x):
                return x

    def keep(self, *args, **kwargs):
        """
        Select elements matching a predicate.
        filter(..., [1,2]) <=> List([1,2]).keep(...)
        """
        f = self._f(*args, **kwargs)
        return self._moka_assign(x for x in self if f(x))

    def rem(self, *args, **kwargs):
        """
        Like 'keep' but remove elements matching the predicate.
        """
        f = self._f(*args, **kwargs)
        return self._moka_assign(x for x in self if not f(x))

    def some(self, *args, **kwargs):
        """
        Return True if at least one item match a predicate.
        List([1,2]).some(lambda x == 2)
        <=>
        any(x == 2 for x in [1,2])
        """
        f = self._f(*args, **kwargs)

        for x in self:
            if f(x):
                return True

        return False

    def all(self, *args, **kwargs):
        """
        Return True if all items match a predicate.
        List([2,2]).all(lambda x == 2)
        <=>
        all(x == 2 for x in [2,2])
        """
        f = self._f(*args, **kwargs)

        for x in self:
            if not f(x):
                return False

        return True

    # aliases
    has = some

    def __getslice__(self, *args, **kwargs):
        """
        List(..)[2:4] returns moka.List instead of builtin list.
        """
        return List(list.__getslice__(self, *args, **kwargs))


(List(['append', 'extend', 'sort', 'reverse', 'insert'])
   .map(List._proxy))


class Dict(dict):
    """
    clone()
    map x,y -> new y
    map()
    keep(),
    rem
    some/has
    all
    count () = len, (x|f)
    empty () == [], (f) -> x in [0, None]..
    Do do(lambda seq: ...)
    invoke

    wrapper: clear(), fromkeys()
       (and last_value = the result of the last operation)
       also do will pass extra arg. so do(self.assertTrue, ...)
       = do(lambda seq: self.assertTrue(seq, ...)
       = self.assertTrue(seq, ...)
    """

    @staticmethod
    def _proxy(method_name):
        def wrap(self, *args, **kwargs):
            inst = Dict(self)
            getattr(dict, method_name)(inst, *args, **kwargs)
            return inst

        setattr(Dict, method_name, wrap)

    def _f(self, f, *args, **kwargs):
        def tmp(x, y):
            return f(x, y, *args, **kwargs)

        return tmp

    def __init__(self, *args, **kwargs):
        self._moka_save = False
        dict.__init__(self, *args, **kwargs)

    def _moka_assign(self, items):
        if self._moka_save:
            pass
        else:
            return Dict(items)

    def clone(self):
        return Dict(self)

    def map(self, *args, **kwargs):
        f = self._f(*args, **kwargs)
        return self._moka_assign(f(x, y) for x, y in self.items())

    def keep(self, *args, **kwargs):
        f = self._f(*args, **kwargs)
        return self._moka_assign((x, y) for x, y in self.items()
                                        if f(x, y))

    def rem(self, *args, **kwargs):
        f = self._f(*args, **kwargs)
        return self._moka_assign((x, y) for x, y in self.items()
                                        if not f(x, y))

    def all(self, *args, **kwargs):
        f = self._f(*args, **kwargs)

        for x, y in self.items():
            if not f(x, y):
                return False

        return True

    def some(self, *args, **kwargs):
        f = self._f(*args, **kwargs)

        for x, y in self.items():
            if f(x, y):
                return True

        return False

    def count(self, *args, **kwargs):
        if not args and not kwargs:
            return len(self)
        else:
            return len(Dict(self).keep(*args, **kwargs))

    def do(self, function, *args, **kwargs):
        self.last_value = function(self, *args, **kwargs)
        return self

    def copy(self):
        return Dict(self)

    @classmethod
    def fromkeys(cls, *args, **kwargs):
        return Dict(dict.fromkeys(*args, **kwargs))

    def empty(self, *args, **kwargs):
        if not args and not kwargs:
            return len(self) == 0
        else:
            return len(Dict(self).rem(*args, **kwargs)) == 0


List(['update', 'clear']).map(Dict._proxy)
