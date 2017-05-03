#!/usr/bin/python
# -*- coding: utf-8 -*-

import copy

class Range(object):

    def __init__(self, start, end):
        self.start = start
        self.end = end

    def get_id(self):
        return '%s-%s' % (self.start, self.end)
        
    def size(self):
        return self.end - self.start

    def merge(self, another):
        return Range(min(self.start, another.start), max(self.end, another.end))

    def shift(self, offset):
        obj = copy.copy(self)
        obj.start += offset
        obj.end += offset
        return obj

    def same_range(self, range):
        return self.start == range.start and self.end == range.end

    def is_overlap(self, another):
        a, b = self, another
        if a.start > b.start:
            a, b = b, a

        return a.end > b.start

    def is_contain(self, another):
        return self.start <= another.start and self.end >= another.end

    def is_cross(self, another):
        return self.is_overlap(another) and not self.is_contain(another)

def build_interval_tree(ranges):
    def tree_insert(node, range):
        for child in node['children']:
            if child['range'].is_contain(range):
                return tree_insert(child, range)

        node['children'].append({
            'range': range,
            'children': []
        })
        node['children'].sort(key=lambda r: r['range'].start)
        return

    """
        The algorithm will construct the tree such that range of subtree is contained in its parent.
        This is greedy algorithm, the algo. will sort ranges by its interval length, and insert one by one to the tree.
        
        Nodes of the returned tree are ranges, except the root of the tree is constructed by the left and right most interval.

        @param ranges list<Range>
        @return { 'range': Range, children: list<Range> }
    """
    left_most_value = min(ranges, key=lambda a: a.start).start
    right_most_value = max(ranges, key=lambda a: a.end).end

    root = {
        'range': Range(left_most_value, right_most_value),
        'is_annotation': False,
        'children': []
    }

    # sort ranges by its length, descending order, and start inserting to the tree until insert all ranges
    ranges = sorted(ranges, key=lambda a: a.end - a.start, reverse=True)
    for range in ranges:
        tree_insert(root, range)

    return root
