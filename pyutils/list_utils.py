#!/usr/bin/python
# -*- coding: utf-8 -*-
from collections import OrderedDict
from typing import List, Any, Iterable, Callable, Union, Dict, Generic
from typing import TypeVar

T = TypeVar('T')
V = TypeVar('V')


def identity(x: Any):
    """Return same value

    Example:
        >>> identity(5)
        5

        >>> identity("hello world")
        'hello world'
    """
    return x


def append2list(c: List[T], v: T) -> List[T]:
    """Append element v to list c, and return list c

    Example:
        >>> append2list(["yellow", "red"], "green")
        ['yellow', 'red', 'green']

        >>> c = ["yellow", "red"]; append2list(c, "green") is c
        True
    """
    c.append(v)
    return c


def unique_values(array: Iterable[T], key: Callable[[T], Union[str, int, float]]=None) -> List[T]:
    """Remove duplication in array, and keep original order

    Example:
        >>> unique_values([5, 4, 1, 4, 3])
        [5, 4, 1, 3]

        >>> unique_values([(5, "yellow"), (4, "green"), (1, "black"), (4, "black"), (3, "pink")], lambda x: x[0])
        [(5, 'yellow'), (4, 'green'), (1, 'black'), (3, 'pink')]
    """
    values = set()
    unique_array = []

    if key is None:
        for v in array:
            if v not in values:
                unique_array.append(v)
                values.add(v)
    else:
        for v in array:
            v_key = key(v)
            if v_key not in values:
                unique_array.append(v)
                values.add(v_key)

    return unique_array


def group_by(array: Iterable[T], key: Callable[[T], Union[str, int, float]]=None, preserve_order: bool=False) -> List[List[T]]:
    """Group elements in an array by its key, optionally preserve order of element

    Example:
        >>> group_by([5, 1, 3, 1, 3, 5, 2])
        [[5, 5], [1, 1], [3, 3], [2]]
        >>> group_by([5, 1, 3, 1, 3, 5, 2], preserve_order=True)
        [[5, 5], [1, 1], [3, 3], [2]]
        >>> group_by([(5, 'a'), (1, 'b'), (3, 'a'), (1, 'a'), (5, 'c'), (2, 'd')], lambda x: x[0])
        [[(5, 'a'), (5, 'c')], [(1, 'b'), (1, 'a')], [(3, 'a')], [(2, 'd')]]
    """

    if preserve_order:
        values: Dict[Union[str, int, float], List[T]] = OrderedDict()
    else:
        values: Dict[Union[str, int, float], List[T]] = {}
    if key is None:
        key = identity

    for v in array:
        v_key = key(v)
        if v_key not in values:
            values[v_key] = []
        values[v_key].append(v)

    return list(values.values())


def flatten(array: Iterable[Iterable[T]]) -> List[T]:
    """Flatten nested list

    Example:
        >>> flatten([[5, 2], [3, 1], [2, 2]])
        [5, 2, 3, 1, 2, 2]
    """
    return [e for es in array for e in es]


class _(Generic[T]):
    """List wrapper to write map/reduce/filter/... function shorter

    Example:
        Chain function to reduce many parentheses to make the code readable
        >>> _([5, 2, 3]).ifilter(lambda x: x % 2 != 0).map(lambda x: x ** 2)
        [25, 9]

        Compare to python3 solution
        >>> list(map(lambda x: x ** 2, filter(lambda x: x % 2 != 0, [5, 2, 3])))
        [25, 9]

        Support looping like normal map/filter object (avoid create unnecessary list)
        >>> for e in _([5, 2, 3]).imap(lambda x: x ** 2): print(e);
        25
        4
        9

        Also support print list
        >>> print(_([5, 2, 3]))
        _([5, 2, 3])
    """

    def __init__(self, array: Union[Iterable[T], List[T]]) -> None:
        self.array: Union[Iterable[T], List[T]] = array

    def get_value(self) -> Union[Iterable[T], List[T]]:
        """Get content of this wrapper"""
        return self.array

    def imap(self, func: Callable[[T], V]) -> '_[V]':
        """Return a wrapped iterator that applies function to every item of iterable, yielding the results

        Example:
            >>> res = _([1, 2, 3]).imap(lambda x: x ** 2)
            >>> assert isinstance(res, _); isinstance(res.array, map)
            True
            >>> list(res.array)
            [1, 4, 9]
        """
        return _(map(func, self.array))

    def ifilter(self, func: Callable[[T], bool]) -> '_[T]':
        """Construct a wrapped iterator from those elements of iterable for which function returns true

        Example:
            >>> res = _([1, 2, 3]).ifilter(lambda x: x % 2 == 0)
            >>> assert isinstance(res, _); isinstance(res.array, filter)
            True
            >>> list(res.array)
            [2]
        """
        return _(filter(func, self.array))

    def map(self, func: Callable[[T], V]) -> 'List[V]':
        """Return new array that every item is result of func

        Example:
            >>> _([1, 2, 3]).map(lambda x: x ** 2)
            [1, 4, 9]
        """
        return [func(v) for v in self.array]

    def filter(self, func: Callable[[T], bool]) -> 'List[T]':
        """Return new array from those elements of original array for which function returns true

        Example
            >>> _([1, 2, 3]).filter(lambda x: x % 2 == 0)
            [2]
        """
        return [v for v in self.array if func(v)]

    def iunique(self, key: Callable[[T], Union[str, int, float]]=None) -> '_[T]':
        """Return a new wrapped array which have no duplication, and keep original order

        Example:
            >>> _([5, 4, 1, 4, 3]).iunique().get_value()
            [5, 4, 1, 3]

            >>> _([(5, "yellow"), (4, "green"), (1, "black"), (4, "black"), (3, "pink")]).iunique(lambda x: x[0]).get_value()
            [(5, 'yellow'), (4, 'green'), (1, 'black'), (3, 'pink')]
        """
        return _(unique_values(self.array, key))

    def unique(self, key: Callable[[T], Union[str, int, float]]=None) -> 'List[T]':
        """Return a new array which have no duplication, and keep original order

        Example:
            >>> _([5, 4, 1, 4, 3]).unique()
            [5, 4, 1, 3]

            >>> _([(5, "yellow"), (4, "green"), (1, "black"), (4, "black"), (3, "pink")]).unique(lambda x: x[0])
            [(5, 'yellow'), (4, 'green'), (1, 'black'), (3, 'pink')]
        """
        return unique_values(self.array, key)

    def forall(self, func: Callable[[T], Any]) -> '_[T]':
        """Apply a function to all element in the wrapper, and return itself

        Example:
            >>> _([[5, 'yellow'], [4, 'green'], [1, 'black', 'hair']]).forall(lambda x: append2list(x, len(x))).tolist()
            [[5, 'yellow', 2], [4, 'green', 2], [1, 'black', 'hair', 3]]
        """
        all(func(x) or True for x in self.array)
        return self

    def all(self, key: Callable[[T], bool]=None) -> bool:
        """Return True if all elements of the wrapper are true (or if the wrapper is empty)

        Example:
            >>> _([1, 2, 3]).all(lambda x: x > 0)
            True
            >>> _([1, 2, -1]).all(lambda x: x > 0)
            False
            >>> _([True, True, True]).all()
            True
        """
        if key is None:
            return all(self.array)
        return all(key(x) for x in self.array)

    def any(self, key: Callable[[T], bool]=None) -> bool:
        """Return True if any element of the wrapper is true. If the wrapper is empty, return False

        Example:
            >>> _([1, 2, 3]).any(lambda x: x < 0)
            False
            >>> _([1, 2, -1]).any(lambda x: x < 0)
            True
            >>> _([False, False, True]).any()
            True
        """
        if key is None:
            return any(self.array)
        return any(key(x) for x in self.array)

    def enumerate(self) -> '_[Tuple[int, T]]':
        """Return a wrapped enumerate object

        Example:
            >>> res = _([1, 2, 3]).enumerate()
            >>> assert isinstance(res, _); list(res.get_value())
            [(0, 1), (1, 2), (2, 3)]
        """
        return _(enumerate(self.array))

    def tolist(self) -> List[T]:
        """Get content of this wrapper, convert to list if necessary

        Example:
            >>> _([1, 2, 3]).enumerate().tolist()
            [(0, 1), (1, 2), (2, 3)]
        """
        if isinstance(self.array, list):
            return self.array
        return list(self.array)

    def flatten(self):
        """Flatten nested list

        Example:
            >>> _([[5, 2], [3, 1], [2, 2]]).flatten().tolist()
            [5, 2, 3, 1, 2, 2]
        """
        return _(flatten(self.array))

    def join(self, delimiter: str) -> str:
        """Join all elements of a list/iterable separated by delimiter. Elements are auto-converted to string by via
        str function

        Example:
            >>> _([5, 2, 1, 2, 3]).join(",")
            '5,2,1,2,3'
        """
        return delimiter.join((str(x) for x in self.array))

    def __str__(self):
        return "_(%s)" % self.array

    def __iter__(self):
        """Return an iterator so that we can use to loop through"""
        return self.array
