#!/usr/bin/python
# -*- coding: utf-8 -*-
from typing import TYPE_CHECKING, Dict, Any

if TYPE_CHECKING:
    from pyutils.graph_utils.graph import Graph
    from pyutils.graph_utils.graph_node import GraphNode


class GraphLink(object):
    def __init__(self, id: str, label: str, source_id: str, dest_id: str) -> None:
        self.graph: Graph = None
        self.id: str = str(id)
        self.label: str = str(label)
        self.source_id: str = str(source_id)
        self.dest_id: str = str(dest_id)

    def clone_values(self):
        init_args = self.__init__.__code__.co_varnames[1:self.__init__.__code__.co_argcount]  # ignore self
        init_args = {arg: self.__dict__[arg] for arg in init_args}
        return self.__class__(**init_args)

    def is_equal(self, link: 'GraphLink') -> bool:
        if link is None:
            return False
        return self.id == link.id and self.label == link.label and self.source_id == link.source_id and self.dest_id == link.dest_id

    def set_graph(self, graph: 'Graph') -> 'GraphLink':
        self.graph = graph
        return self

    def get_id(self) -> str:
        return self.id

    def get_printed_label(self):
        return "%s: %s" % (self.id, self.label)

    def get_source_node(self) -> 'GraphNode':
        return self.graph.get_node_by_id(self.source_id)

    def get_dest_node(self) -> 'GraphNode':
        return self.graph.get_node_by_id(self.dest_id)

    def has_attributes(self, attrs: Dict[str, Any]) -> bool:
        for attr, attr_val in attrs.items():
            if attr not in self.__dict__ or self.__dict__[attr] != attr_val:
                return False
        return True

    def is_self_reference(self) -> bool:
        return self.source_id == self.dest_id

    def __getitem__(self, attr: str) -> Any:
        return self.__dict__[attr]

    def __repr__(self) -> str:
        return '%s(label=%s, id=%s, source_id=%s, dest_id=%s)' % (self.__class__.__name__, self.label, self.id,
                                                                  self.source_id, self.dest_id)


class WeightedGraphLink(GraphLink):
    def __init__(self, id: str, label: str, source_id: str, dest_id: str, weight: float) -> None:
        super().__init__(id, label, source_id, dest_id)
        self.weight = weight

    @classmethod
    def from_graph_link(cls, l: GraphLink, weight: float) -> 'WeightedGraphLink':
        init_args = l.__class__.__init__.__code__.co_varnames[1:
                                                              l.__class__.__init__.__code__.co_argcount]  # ignore self
        init_args = {arg: l.__dict__[arg] for arg in init_args}
        init_args['weight'] = weight
        weighted_link = cls(**init_args)
        return weighted_link

    def get_printed_label(self):
        return "%s: %s\nweight=%s" % (self.id, self.label, self.weight)
