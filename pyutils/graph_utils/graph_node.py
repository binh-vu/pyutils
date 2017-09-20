#!/usr/bin/python
# -*- coding: utf-8 -*-
from collections import OrderedDict
from typing import Dict, Any, TYPE_CHECKING, Generator, List

if TYPE_CHECKING:
    from pyutils.graph_utils.graph import Graph
    from pyutils.graph_utils.graph_link import GraphLink


class GraphNode(object):

    def __init__(self, id: str, label: str) -> None:
        self.graph: Graph = None
        self.id: str = str(id)
        self.label: str = str(label)

        self.outgoing_links: Dict[str, GraphLink] = OrderedDict()
        self.incoming_links: Dict[str, GraphLink] = OrderedDict()

    def clone_values(self):
        init_args = self.__init__.__code__.co_varnames[1:self.__init__.__code__.co_argcount]  # ignore self
        init_args = {arg: self.__dict__[arg] for arg in init_args}
        return self.__class__(**init_args)

    def is_equal(self, node: 'GraphNode') -> bool:
        if node is None:
            return False
        return self.id == node.id and self.label == node.label

    def set_graph(self, graph: 'Graph') -> 'GraphNode':
        self.graph = graph
        return self

    def get_id(self) -> str:
        return self.id

    def get_printed_label(self) -> str:
        return "%s: %s" % (self.id, self.label)

    def add_outgoing_link(self, link: 'GraphLink') -> 'GraphNode':
        self.outgoing_links[link.get_id()] = link
        return self

    def remove_outgoing_link(self, link_id: str) -> 'GraphNode':
        del self.outgoing_links[link_id]
        return self

    def add_incoming_link(self, link: 'GraphLink') -> 'GraphNode':
        self.incoming_links[link.get_id()] = link
        return self

    def remove_incoming_link(self, link_id: str) -> 'GraphNode':
        del self.incoming_links[link_id]
        return self

    def iter_outgoing_links_by_attrs(self, **k_attrs: Any) -> Generator['GraphLink', None, None]:
        if len(k_attrs) == 0:
            for link in self.outgoing_links.values():
                yield link
        else:
            for link in self.outgoing_links.values():
                if link.has_attributes(k_attrs):
                    yield link

    def get_outgoing_links_by_attrs(self, **k_attrs: Any) -> List['GraphLink']:
        return list(self.iter_outgoing_links_by_attrs(**k_attrs))

    def iter_incoming_links_by_attrs(self, **k_attrs) -> Generator['GraphLink', None, None]:
        if len(k_attrs) == 0:
            for link in self.incoming_links.values():
                yield link
        else:
            for link in self.incoming_links.values():
                if link.has_attributes(k_attrs):
                    yield link

    def get_incoming_links_by_attrs(self, **k_attrs: Any) -> List['GraphLink']:
        return list(self.iter_incoming_links_by_attrs(**k_attrs))

    def __getitem__(self, attr: str) -> Any:
        return self.__dict__[attr]

    def __repr__(self) -> str:
        return '%s(label=%s, id=%s)' % (self.__class__.__name__, self.label, self.id)
