from typing import List


class NodeDto:
    def __init__(self, _name: str, _children=None):
        if _children is None:
            _children = []
        self._name: str = _name
        self._children: List['NodeDto'] = _children

    @property
    def children(self):
        return self._children

    @property
    def name(self):
        return self._name


class TreeDto:
    def __init__(self, root_node: NodeDto):
        self._root_node = root_node

    @property
    def root_node(self):
        return self._root_node
