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
    """List wrapper to write map/reduce/filter function shorter

    Example:
        >>>
    """

    def __init__(self, array: Union[Iterable[T], List[T]]) -> None:
        self.array: Union[Iterable[T], List[T]] = array

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

    def __iter__(self):
        """Return an iterator so that we can use to loop through"""
        return self.array
