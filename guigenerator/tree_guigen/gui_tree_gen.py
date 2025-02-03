"""Build a tree of widgets from widget_tree.json
tree_widgets_description.json contains a list of possible widgets types used
for tree guigen.
It has a list with type-object, each has following parameters:
* name (str) -- widgets's type name.
* container (bool) -- false means that the widgets as a node in the tree
cant have any children.
  i.e can't contain other widgets (for example button, label etc.)
* prob (float) -- probability of node occurrence in the tree.
* accept (List[str]) -- contains widgets that can be accepted as a child of
the current widgets.
  If list is empty, then any widgets can be accepted.

Script parameters:
* treesize -- required param. Specifies number of generated nodes in the tree.
* --input -- not required param. Specifies the name and path for the input
json file
* --output -- not required param. Specifies the name and path for the output
json file
"""

import argparse
import sys
from pathlib import Path
from random import randrange, shuffle
from typing import List, Any, Set, NoReturn, Tuple

from guigenerator.dto.tree_dto import TreeDto, NodeDto
from guigenerator.dto.widget_description_dto import WidgetDescriptionDto
from guigenerator.utils import Utils


class TreeGeneration:
    WIDGETS_PATH: Path = Utils.PROJ_ROOT_DIR / Path(
        "temp/tree_widgets_description.json")
    OUTPUT_FILE_NAME: Path = Utils.PROJ_ROOT_DIR / Path(
        "temp/trees/widget_tree.json")

    @classmethod
    def generate_trees(cls, number_of_trees: int,
                       nmb_of_widgets_range: Tuple[int, int]):
        from random import randint

        number_of_widgets = randint(*nmb_of_widgets_range)

        for tree_number in range(number_of_trees):
            tree_name = f"tree{tree_number + 1}.json"
            output_ = cls.OUTPUT_FILE_NAME.parent / Path(tree_name)
            cls.generate_tree(number_of_widgets, str(cls.WIDGETS_PATH),
                              str(output_))

    @classmethod
    def generate_tree(cls, number_of_widgets: int,
                      input_path: str = WIDGETS_PATH,
                      output_path: str = OUTPUT_FILE_NAME):
        possible_widgets_dto: List[WidgetDescriptionDto] \
            = Utils.read_from_json(input_path,
                                   object_hook_
                                   =lambda d: WidgetDescriptionDto(**d))
        possible_widgets = [
            TreeWidgetDescriptionUtils.get_widget_desc_from_dto(dto) for dto in
            possible_widgets_dto]
        tree: Tree = Tree(possible_widgets, number_of_widgets)
        Utils.write_to_json(tree.as_dto().root_node, output_path)

    @classmethod
    def generate_empty_tree(cls, input_path: str = WIDGETS_PATH,
                            output_path: str = OUTPUT_FILE_NAME):
        cls.generate_tree(0, input_path, output_path)

class TreeWidgetDescription:
    def __init__(self, _name: str, _container: bool, _prob: float,
                 _solo: bool = False, _accept_list: List[str] = None,
                 _has_only_child: bool = False):
        if _accept_list is None:
            _accept_list = []
        self._name: str = _name
        self._container: bool = _container
        self._has_only_child: bool = _has_only_child
        self._solo: bool = _solo
        self._prob: float = _prob
        self._accept_list: List[str] = _accept_list

    @property
    def is_container(self) -> bool:
        return self._container

    @property
    def is_solo(self) -> bool:
        return self._solo

    @property
    def has_only_child(self) -> bool:
        return self._has_only_child

    @property
    def name(self) -> str:
        return self._name

    @property
    def prob(self) -> float:
        return self._prob

    @property
    def accept_list(self) -> List[str]:
        return self._accept_list

    @property
    def is_accepting_any_widget(self) -> bool:
        return self._accept_list.__len__() == 0

    def can_accept(self, other_widget: 'TreeWidgetDescription') -> bool:
        return other_widget.name in self._accept_list

    def __repr__(self):
        return f"<Widget object - name: {self.name}; container:" \
               f"{self._container}; sole: {self.is_solo}; " \
               f"only_child: {self.has_only_child}; prob: {self.prob}; " \
               f"accept_list: {self.accept_list}>"


class Tree:
    def __init__(self, reference_widgets: List[TreeWidgetDescription],
                 number_of_widgets):
        self._tree: 'Node' = self._create_tree(reference_widgets,
                                               number_of_widgets)

    @property
    def tree(self) -> 'Node':
        return self._tree

    def _create_tree(self, ref_widgets: List[TreeWidgetDescription],
                     number_of_widgets: int) -> 'Node':
        root_widget: TreeWidgetDescription = \
            TreeWidgetDescriptionUtils.get_first_container_widget(
                ref_widgets)
        sample_nodes = WidgetsSample.create_sample(ref_widgets, root_widget,
                                                   number_of_widgets)
        tree: Node = self._build_tree(sample_nodes)
        shuffle(tree.children)
        return tree

    @classmethod
    def _build_tree(cls, widgets: List[TreeWidgetDescription]):
        container_nodes: List[
            Node] = TreeWidgetDescriptionUtils.get_container_widgets_as_nodes(
            widgets)
        while len(container_nodes) > 1:
            cls._link_two_container_nodes(container_nodes)
        tree_of_containers: Node = TreeWidgetDescriptionUtils.get_first_node(
            container_nodes)

        ordinary_tree_nodes: List[
            Node] = TreeWidgetDescriptionUtils.get_ordinary_widgets_as_nodes(
            widgets)
        container_tree_nodes = tree_of_containers.get_node_and_children()
        while len(ordinary_tree_nodes) > 0:
            cls._link_ordinary_node_to_container_node(container_tree_nodes,
                                                      ordinary_tree_nodes)

        cls.remove_empty_containers(tree_of_containers)
        return tree_of_containers

    @classmethod
    def _link_ordinary_node_to_container_node(cls, container_tree_nodes: List[
        'Node'],
                                              ordinary_tree_nodes: List[
                                                  'Node']):
        parent_index: int = randrange(0, len(container_tree_nodes))
        child_index: int = randrange(0, len(ordinary_tree_nodes))

        child = ordinary_tree_nodes[child_index]
        parent = container_tree_nodes[parent_index]

        if parent.can_be_parent_of(child) and cls._only_child_check(parent):
            parent.children.append(child)
            ordinary_tree_nodes.pop(child_index)

    @classmethod
    def _only_child_check(cls, parent: 'Node') -> bool:
        return not parent.widget.has_only_child \
               or (parent.widget.has_only_child and len(parent.children) == 0)

    @classmethod
    def _link_two_container_nodes(cls, container_nodes: List['Node']):
        parent_index: int = randrange(0, len(container_nodes))
        child_index: int = randrange(0, len(container_nodes))
        if parent_index != child_index:
            parent_node = container_nodes[parent_index]
            child_node = container_nodes[child_index]

            if parent_node.can_be_parent_of(child_node):
                parent_node.children.append(child_node)
                cls._link_only_children(child_index, child_node,
                                        container_nodes)
                container_nodes.remove(child_node)

    @classmethod
    def _link_only_children(cls, node_index, node, container_nodes):
        possible_only_grandchildren = \
            cls._get_container_nodes_having_given_as_only_parent(
                node_index, container_nodes)
        for grandchild_node in possible_only_grandchildren:
            node.children.append(grandchild_node)
            container_nodes.remove(grandchild_node)

    @classmethod
    def _get_container_nodes_having_given_as_only_parent(cls,
                                                         parent_index: int,
                                                         container_nodes: List[
                                                             'Node']) \
            -> List['Node']:
        potential_only_parent_nodes: List['Node'] \
            = [node for node in container_nodes if
               node.widget.name in container_nodes[
                   parent_index].widget.accept_list]
        only_parent_nodes: List['Node'] = []

        for potential_only_parent_node in potential_only_parent_nodes:
            ok = False
            for other_node_index, other_node in enumerate(container_nodes):
                if parent_index != other_node_index:
                    if potential_only_parent_node in other_node.children:
                        ok = True
                        break
            if not ok:
                only_parent_nodes.append(potential_only_parent_node)
        return only_parent_nodes

    @classmethod
    def remove_empty_containers(cls, tree_of_containers: 'Node'):
        def traversal1(node: Node):
            node_child_index = 0
            while node_child_index < len(node.children):
                node_child = node.children[node_child_index]
                if node_child.widget.is_container:
                    traversal1(node_child)
                if node_child.widget.is_container and not node_child.children:
                    node.children.pop(node_child_index)
                    node_child_index -= 1
                node_child_index += 1

        def traversal(child_node: Node, parent_node: Node):
            for grandchild_node in child_node.children:
                if grandchild_node.widget.is_container:
                    traversal(grandchild_node, child_node)

            if not child_node.children:
                parent_node.children.remove(child_node)

        traversal1(tree_of_containers)

    def as_dto(self) -> TreeDto:
        def traversal(node_orig: Node, node_dto: NodeDto):
            for child_orig in node_orig.children:
                child_dto: NodeDto = NodeDto(child_orig.widget.name)
                node_dto.children.append(child_dto)
                if child_orig.widget.is_container:
                    traversal(child_orig, child_dto)

        root_node: Node = self._tree
        root_node_dto: NodeDto = NodeDto(root_node.widget.name)
        traversal(root_node, root_node_dto)

        return TreeDto(root_node_dto)

    def __str__(self):
        def traversal(node: Node, level: int) -> None:
            result_string_list.append(("    " * level)
                                      + f"<level {level}>::{node.widget}"
                                      + f"::<amount of children "
                                        f"{len(node.children)}>")
            for child_node in node.children:
                traversal(child_node, level + 1)

        result_string_list = []
        traversal(self._tree, 0)
        result_string_list.append("<------>")
        return '\n'.join(result_string_list)


class Node:
    def __init__(self, _widget: TreeWidgetDescription,
                 _children: List['Node'] = None):
        self._widget: TreeWidgetDescription = _widget
        self._children: List[
            'Node'] = list() if _children is None else _children

    @property
    def widget(self) -> TreeWidgetDescription:
        return self._widget

    @property
    def children(self) -> List['Node']:
        return self._children

    def can_be_parent_of(self, child: 'Node') -> bool:
        return self.widget.is_container \
               and (
                       self.widget.is_accepting_any_widget or
                       self.widget.can_accept(
                           child.widget))

    def get_node_and_children(self) -> List['Node']:
        def dfs(ls: List['Node'], node: 'Node') -> NoReturn:
            ls.append(node)
            for child in node.children:
                dfs(ls, child)

        result = []
        dfs(result, self)
        return result

    def __repr__(self):
        return f'\n<Body: {self._widget.__repr__()} \nChildren: ' \
               f'{self._children}>'


class WidgetsSample:
    @classmethod
    def create_sample(cls, ref_widgets: List[TreeWidgetDescription],
                      root_widget: TreeWidgetDescription,
                      number_of_widgets: int) -> List[TreeWidgetDescription]:
        accepted_widget_names: Set[str] \
            = set(accepted_widget_name for accepted_widget_name in
                  root_widget.accept_list)
        probabilities: List[float] = [rw.prob for rw in ref_widgets]
        widgets_sample: List[TreeWidgetDescription] = [root_widget]
        while len(widgets_sample) < number_of_widgets:
            cls._generate_widget_node(accepted_widget_names, probabilities,
                                      ref_widgets, widgets_sample)

        cls._fix_only_child_widgets_number_ratio(widgets_sample)

        return widgets_sample

    @classmethod
    def _generate_widget_node(cls, accepted_widget_names, probabilities,
                              ref_widgets, widgets_sample):
        from random import choices
        rand_widget: TreeWidgetDescription = \
            choices(ref_widgets, weights=probabilities, k=1)[0]
        if rand_widget.name in accepted_widget_names \
                and cls._solo_checked(rand_widget, widgets_sample):
            widgets_sample.append(rand_widget)
            accepted_widget_names.update(rand_widget.accept_list)

    @classmethod
    def _solo_checked(cls, widget, widget_sample):
        return not widget.is_solo or (
                widget.is_solo and widget_sample.count(widget) == 0)

    @classmethod
    def _fix_only_child_widgets_number_ratio(cls, widgets_sample: List[
        TreeWidgetDescription]):
        # DUMB VERSION
        parent_child_names = set(
            (w.name, w.accept_list[0]) for w in widgets_sample if
            w.has_only_child)
        names = [widget.name for widget in widgets_sample]
        for p_name, c_name in parent_child_names:
            p_count = names.count(p_name)
            c_count = names.count(c_name)
            while c_count > p_count:
                index = names.index(c_name)
                names.pop(index)
                widgets_sample.pop(index)
                c_count -= 1


class TreeWidgetDescriptionUtils:
    @classmethod
    def get_ordinary_widgets(cls, widgets: List[TreeWidgetDescription]) -> \
            List[TreeWidgetDescription]:
        return [wd for wd in widgets if not wd.is_container]

    @classmethod
    def get_ordinary_widgets_as_nodes(cls,
                                      widgets: List[TreeWidgetDescription]) \
            -> \
                    List[Node]:
        return [Node(wd) for wd in widgets if not wd.is_container]

    @classmethod
    def get_container_widgets(cls, widgets: List[TreeWidgetDescription]) -> \
            List[TreeWidgetDescription]:
        return [wd for wd in widgets if wd.is_container]

    @classmethod
    def get_container_widgets_as_nodes(cls,
                                       widgets: List[TreeWidgetDescription]) \
            -> \
                    List[Node]:
        return [Node(wd) for wd in widgets if wd.is_container]

    @classmethod
    def get_first_container_widget(cls, widgets: List[
        TreeWidgetDescription]) -> TreeWidgetDescription:
        return TreeWidgetDescriptionUtils.get_container_widgets(widgets)[0]

    @classmethod
    def get_first_node(cls, nodes: List[Node]) -> Node:
        return nodes[0]

    @classmethod
    def get_widget_desc_from_dto(cls, dto: WidgetDescriptionDto):
        return TreeWidgetDescription(dto.name, dto.container, dto.prob,
                                     dto.solo, dto.accept_list,
                                     dto.has_only_child)


def _parse_args(args=None) -> Any:
    if args is None:
        args = sys.argv[1:]

    parser = argparse.ArgumentParser(
        description=sys.modules[__name__].__doc__)

    parser.add_argument("treesize", type=int,
                        help="The amount of widgets that are used in tree "
                             "guigen")
    parser.add_argument("--input", type=str,
                        default=TreeGeneration.WIDGETS_PATH,
                        help="define input: {file_path}/{file_name}.json")
    parser.add_argument("--output", type=str,
                        default=TreeGeneration.OUTPUT_FILE_NAME,
                        help="define output: {file_path}/{file_name}.json")

    return parser.parse_args(args)


if __name__ == '__main__':
    options = _parse_args()
    TreeGeneration.generate_tree(options.treesize, options.input,
                                 options.output)
