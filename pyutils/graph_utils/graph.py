#!/usr/bin/python
# -*- coding: utf-8 -*-
from collections import OrderedDict, defaultdict, deque
from typing import List, Set, Dict, Any, Generator, Union, Generic, TypeVar

from orderedset import OrderedSet

from pyutils.graph_utils.graph_link import GraphLink
from pyutils.graph_utils.graph_node import GraphNode

NodeType = TypeVar('GraphNode', covariant=True, bound=GraphNode)
LinkType = TypeVar('GraphLink', covariant=True, bound=GraphLink)


class Graph(Generic[NodeType, LinkType]):
    def __init__(self, node_index_attributes: List[str]=None, link_index_attributes: List[str]=None) -> None:
        """
        :param node_index_attributes: node's attributes to be indexed
        :param link_index_attributes: link's attributes to be indexed, to index attributes belong to source & dest node, use prefix _source_ & _dest_
        """
        if node_index_attributes is None:
            node_index_attributes = []

        if link_index_attributes is None:
            link_index_attributes = []

        self.node_index_attributes: List[str] = list(OrderedSet(node_index_attributes))
        self.link_index_attributes: List[str] = list(OrderedSet(link_index_attributes))
        self.node_index: Dict[str, Dict[Any, Set[str]]] = {attr: {} for attr in self.node_index_attributes}
        self.link_index: Dict[str, Dict[Any, Set[str]]] = {attr: {} for attr in self.link_index_attributes}
        self.nodes: Dict[str, NodeType] = OrderedDict()
        self.links: Dict[str, LinkType] = OrderedDict()

    def clone_values(self) -> 'Graph[NodeType, LinkType]':
        init_args = self.__init__.__code__.co_varnames[1:self.__init__.__code__.co_argcount]  # ignore self
        init_args = {arg: self.__dict__[arg] for arg in init_args}
        graph = self.__class__(**init_args)
        for node in self.nodes.values():
            graph.add_node(node.clone_values())

        for link in self.links.values():
            graph.add_link(link.clone_values())
        return graph

    def generate_node_id(self, prefix: str='') -> str:
        count = len(self.nodes)
        if prefix != '':
            prefix = '-' + prefix
        id = 'N%s%03d' % (prefix, count)
        assert id not in self.nodes, 'The generated id: %s is already defined' % id
        return id

    def generate_link_id(self, prefix: str='') -> str:
        count = len(self.links)
        if prefix != '':
            prefix = '-' + prefix
        id = 'L%s%03d' % (prefix, count)
        assert id not in self.links, 'The generated id: %s is already defined' % id
        return id

    def index_nodes(self, index_attributes: List[str]) -> None:
        self.node_index_attributes: List[str] = list(OrderedSet(index_attributes))
        self.node_index: Dict[str, Dict[Any, Set[str]]] = {attr: {} for attr in self.node_index_attributes}

        for node in self.nodes.values():
            for attr in self.node_index_attributes:
                if node[attr] not in self.node_index[attr]:
                    self.node_index[attr][node[attr]] = OrderedSet()
                self.node_index[attr][node[attr]].add(node.get_id())

    def index_links(self, link_attributes: List[str]) -> None:
        self.link_index_attributes = link_attributes
        self.link_index: Dict[str, Any] = {attr: {} for attr in self.link_index_attributes}

        for link in self.links.values():
            source = self.nodes[link.get_source_node().get_id()]
            dest = self.nodes[link.get_dest_node().get_id()]
            for attr in self.link_index_attributes:
                if attr.startswith('_source_'):
                    source_attr = attr[len('_source_'):]
                    if source[source_attr] not in self.link_index[attr]:
                        self.link_index[attr][source[source_attr]] = OrderedSet()
                    self.link_index[attr][source[source_attr]].add(link.get_id())
                elif attr.startswith('_dest_'):
                    dest_attr = attr[len('_dest_'):]
                    if dest[dest_attr] not in self.link_index[attr]:
                        self.link_index[attr][dest[dest_attr]] = OrderedSet()
                    self.link_index[attr][dest[dest_attr]].add(link.get_id())
                else:
                    if link[attr] not in self.link_index[attr]:
                        self.link_index[attr][link[attr]] = OrderedSet()
                    self.link_index[attr][link[attr]].add(link.get_id())

    def add_node(self, node: NodeType) -> 'Graph':
        assert node.get_id() not in self.nodes, 'Node\'s already in the graph'
        self.nodes[node.get_id()] = node
        node.set_graph(self)

        for attr in self.node_index_attributes:
            if node[attr] not in self.node_index[attr]:
                self.node_index[attr][node[attr]] = OrderedSet()

            self.node_index[attr][node[attr]].add(node.get_id())

        return self

    def remove_node(self, node_id: str) -> 'Graph':
        assert node_id in self.nodes
        node = self.nodes[node_id]

        # remove from index
        for attr in self.node_index_attributes:
            self.node_index[attr][node[attr]].remove(node.get_id())

        # remove links
        for lid in node.outgoing_links:
            self.remove_link(lid)
        for lid in node.incoming_links:
            self.remove_link(lid)
        del self.nodes[node.get_id()]

        return self

    def add_link(self, link: LinkType) -> 'Graph':
        assert link.get_id() not in self.links, 'Link\'s already in the graph'
        self.links[link.get_id()] = link
        link.set_graph(self)

        source = self.nodes[link.get_source_node().get_id()]
        dest = self.nodes[link.get_dest_node().get_id()]

        source.add_outgoing_link(link)
        dest.add_incoming_link(link)

        for attr in self.link_index_attributes:
            if attr.startswith('_source_'):
                source_attr = attr[len('_source_'):]
                if source[source_attr] not in self.link_index[attr]:
                    self.link_index[attr][source[source_attr]] = OrderedSet()
                self.link_index[attr][source[source_attr]].add(link.get_id())
            elif attr.startswith('_dest_'):
                dest_attr = attr[len('_dest_'):]
                if dest[dest_attr] not in self.link_index[attr]:
                    self.link_index[attr][dest[dest_attr]] = OrderedSet()
                self.link_index[attr][dest[dest_attr]].add(link.get_id())
            else:
                if link[attr] not in self.link_index[attr]:
                    self.link_index[attr][link[attr]] = OrderedSet()
                self.link_index[attr][link[attr]].add(link.get_id())

        return self

    def remove_link(self, link_id: str) -> 'Graph':
        assert link_id in self.links
        link = self.links[link_id]
        for attr in self.link_index_attributes:
            if attr.startswith('_source_'):
                source_attr = attr[len('_source_'):]
                self.link_index[attr][link.get_source_node()[source_attr]].remove(link.get_id())
            elif attr.startswith('_dest_'):
                dest_attr = attr[len('_dest_'):]
                self.link_index[attr][link.get_dest_node()[dest_attr]].remove(link.get_id())
            else:
                self.link_index[attr][link[attr]].remove(link.get_id())

        link.get_source_node().remove_outgoing_link(link.get_id())
        link.get_dest_node().remove_incoming_link(link.get_id())

        return self

    def get_node_by_id(self, id: str) -> NodeType:
        return self.nodes[id]

    def get_link_by_id(self, id: str) -> LinkType:
        return self.links[id]

    def has_node_with_id(self, id: str) -> bool:
        return id in self.nodes

    def has_link_with_id(self, id: str) -> bool:
        return id in self.links

    def __contains__(self, item: Union[NodeType, LinkType]):
        if isinstance(item, GraphNode):
            return item.id in self.nodes
        if isinstance(item, GraphLink):
            return item.id in self.links
        raise Exception('Cannot find item that is neither a node or a link')

    def get_root_nodes(self) -> List[NodeType]:
        return [n for n in self.nodes.values() if len(n.incoming_links) == 0]

    def get_isolated_nodes(self) -> List[NodeType]:
        return [n for n in self.nodes.values() if len(n.incoming_links) == 0 and len(n.outgoing_links) == 0]

    def iter_nodes_by_attrs(self, **k_attrs: Any) -> Generator[NodeType, None, None]:
        matched_nodes = None

        if len(k_attrs) == 0:
            for node in self.nodes.values():
                yield node
        else:
            for attr, value in k_attrs.items():
                assert attr in self.node_index, 'Attr `%s` must be indexed before search' % attr

                if value not in self.node_index[attr]:
                    matched_nodes = OrderedSet()
                    break
                else:
                    tmp = self.node_index[attr][value]

                if matched_nodes is None:
                    matched_nodes = tmp
                else:
                    matched_nodes = matched_nodes.intersection(tmp)

            for node_id in matched_nodes:
                yield self.nodes[node_id]

    def get_nodes_by_attrs(self, **k_attrs: Any) -> List[NodeType]:
        return list(self.iter_nodes_by_attrs(**k_attrs))

    def iter_bfs(self) -> Generator[LinkType, None, None]:
        roots = self.get_root_nodes()
        assert len(roots) > 0
        visited: Set[str] = set()
        queue = deque()
        for root in roots:
            queue.append(root)

        while len(queue) > 0:
            node: NodeType = queue.popleft()
            if node.id in visited:
                continue

            visited.add(node.id)
            for link in node.outgoing_links.values():
                queue.append(link.get_dest_node())

            yield node

    def iter_links_by_attrs(self, **k_attrs: Any) -> Generator[LinkType, None, None]:
        matched_links = None

        if len(k_attrs) == 0:
            for link in self.links.values():
                yield link
        else:
            for attr, value in k_attrs.items():
                assert attr in self.link_index, 'Attr %s must be indexed before search' % attr

                if value not in self.link_index[attr]:
                    matched_links = OrderedSet()
                    break
                else:
                    tmp = self.link_index[attr][value]

                if matched_links is None:
                    matched_links = tmp
                else:
                    matched_links = matched_links.intersection(tmp)

            for link_id in matched_links:
                yield self.links[link_id]

    def get_links_by_attrs(self, **k_attrs: Any) -> List[LinkType]:
        return list(self.iter_links_by_attrs(**k_attrs))

    def is_equal(self, graph: 'Graph[NodeType, LinkType]') -> bool:
        if graph is None:
            return False
        if len(self.nodes) != len(graph.nodes):
            return False
        if len(self.links) != len(graph.links):
            return False

        for node in self.nodes.values():
            if not graph.has_node_with_id(node.id) or not node.is_equal(graph.get_node_by_id(node.id)):
                return False

        for link in self.links.values():
            if not graph.has_link_with_id(link.id) or not link.is_equal(graph.get_link_by_id(link.id)):
                return False
        return True

    def contain_tree(self, tree: 'Graph[NodeType, LinkType]') -> bool:
        def contain_tree_at(tree: GraphNode, graph: 'Graph[NodeType, LinkType]', node: GraphNode) -> bool:
            """This algorithm do greedy choice, when they select links to match, if corresponding subtree is matched then that link is what they think is correct"""
            if node.label != tree.label:
                return False

            index_outgoing_links: Dict[str, Set[GraphLink]] = defaultdict(lambda: set())
            for l in node.outgoing_links.values():
                index_outgoing_links[l.label].add(l)

            selected_links: Set[GraphLink] = set()

            for link in tree.outgoing_links.values():
                matched_links = index_outgoing_links[link.label].difference(selected_links)
                if len(matched_links) == 0:
                    return False
                for matched_link in matched_links:
                    if contain_tree_at(link.get_dest_node(), graph, matched_link.get_dest_node()):
                        # greedy choice
                        selected_links.add(matched_link)
                        break
                else:
                    return False
            return True

        root: NodeType = tree.get_root_nodes()[0]
        for r in self.get_nodes_by_attrs(label=root.label):
            if contain_tree_at(root, self, r):
                return True

        return False
