from enum import Enum
from typing import List, Dict

# name type: str
class AttrName(Enum):
    CHECKABLE = (0, "checkable", ('unchecked', 'checked'))
    ENABLEABLE = (1, "enableable", ('disabled', 'enabled'))
    VSCROLABLE = (2, "vscrolable", ('vert_unscrollable', 'vert_scrollable'))
    HSCROLABLE = (3, "hscrolable", ('hor_unscrollable', 'hor_scrollable'))
    HAS_TEXT = (4, "has_text", ('not_has_text', 'has_text'))
    ICONED = (5, "iconed", ('not_iconed', 'iconed'))
    TYPE = (6, "type", ('text', 'combobox'))
    TEXT = (7, "text", None)

    def __new__(cls, val, fancy_name, state_names):
        obj = object.__new__(cls)
        obj._value_ = val
        obj._fancy_name = fancy_name
        obj._state_names = state_names
        return obj

    @property
    def state_names(self):
        return self._state_names

    @property
    def fancy_name(self):
        return self._fancy_name

    def get_state_index_by_name(self, name: str):
        for state_n, state_name in enumerate(self.state_names):
            if state_name == name:
                return state_n
        raise RuntimeError("Name is not found")

    def get_state_name_by_index(self, index: int):
        return self.state_names[index]


class Attr:
    def __init__(self, name: AttrName, state: [int, str]):
        self._state = state
        self._name = name

    @property
    def name(self) -> AttrName:
        return self._name

    @property
    def state(self) -> [int, str]:
        return self._state

    @property
    def state_name(self) -> str:
        if self.name.state_names is None:
            return self.state
        else:
            return self.name.state_names[self.state]

    @property
    def state_names(self) -> List[str]:
        return self.name.state_names

    def __repr__(self):
        return f"<Name: {self.name} State: {self.state}>"

    def __str__(self):
        return f"<Name: {self.name.name} State: {self.state_name}>"


class AttrHolderBuilder:
    def __init__(self):
        self._widg_attrs: Dict[AttrName, Attr] = {}

    def has_text(self, state: int = 0):
        name = AttrName.HAS_TEXT
        self._widg_attrs[name] = Attr(name, state)
        return self

    def text(self, state: str = ""):
        name = AttrName.TEXT
        self._widg_attrs[name] = Attr(name, state)
        return self

    def iconed(self, state: int = 0):
        name = AttrName.ICONED
        self._widg_attrs[name] = Attr(name, state)
        return self

    def checkable(self, state: int = 0):
        name = AttrName.CHECKABLE
        self._widg_attrs[name] = Attr(name, state)
        return self

    def enableable(self, state: int = 0):
        name = AttrName.ENABLEABLE
        self._widg_attrs[name] = Attr(name, state)
        return self

    def vscrollable(self, state: int = 0):
        name = AttrName.VSCROLABLE
        self._widg_attrs[name] = Attr(name, state)
        return self

    def hscrollable(self, state: int = 0):
        name = AttrName.HSCROLABLE
        self._widg_attrs[name] = Attr(name, state)
        return self

    def type(self, state: int = 0):
        name = AttrName.TYPE
        self._widg_attrs[name] = Attr(name, state)

    def build(self) -> 'AttrHolder':
        return AttrHolder(self._widg_attrs)


class AttrHolder:
    def __init__(self, attrs: Dict[AttrName, Attr] = None):
        if attrs is None:
            attrs = {}
        self._widg_attrs: Dict[AttrName, Attr] = attrs

    def add_attr(self, attr: Attr):
        self._widg_attrs[attr.name] = attr

    def get_attr_list(self) -> List[Attr]:
        return list(self._widg_attrs.values())

    def get_attr(self, name: AttrName) -> Attr:
        return self._widg_attrs[name]



