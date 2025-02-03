from typing import List


class WidgetDescriptionDto:
    def __init__(self, _name: str, _container: bool, _prob: float, _min_width: int = 0, _min_height: int = 0,
                 _solo: bool = False, _accept_list: List[str] = None, _has_only_child: bool = False,
                 _central_widget_child: bool = False, _padding: int = -1):
        if _accept_list is None:
            _accept_list = []
        self._name: str = _name
        self._container: bool = _container
        self._has_only_child: bool = _has_only_child
        self._solo: bool = _solo
        self._prob: float = _prob
        self._accept_list: List[str] = _accept_list
        self._min_width: int = _min_width
        self._min_height: int = _min_height
        self._central_widget_child = _central_widget_child
        self._padding = _padding

    @property
    def name(self) -> str:
        return self._name

    @property
    def container(self) -> bool:
        return self._container

    @property
    def has_only_child(self) -> bool:
        return self._has_only_child

    @property
    def solo(self) -> bool:
        return self._solo

    @property
    def prob(self) -> float:
        return self._prob

    @property
    def accept_list(self) -> List[str]:
        return self._accept_list

    @property
    def min_width(self) -> int:
        return self._min_width

    @property
    def min_height(self) -> int:
        return self._min_height

    @property
    def central_widget_child(self) -> bool:
        return self._central_widget_child

    @property
    def padding(self):
        return self._padding
