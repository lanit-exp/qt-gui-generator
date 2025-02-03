from abc import ABC, abstractmethod
from typing import List, NoReturn

from PySide6 import QtWidgets as QtW

from guigenerator.qt_guigen.widgets.attributes import AttrHolder, Attr, AttrName
from guigenerator.qt_guigen.widgets.widget_names import WidgetNames
from guigenerator.qt_guigen.widgets.widget_geometry import WidgetGeometryAbsFactory, WidgetGeometry
from guigenerator.qt_guigen.widgets import GeometryOutputDataFormat
from guigenerator.qt_guigen.widgets.widget_vals import WidgetContentName, WidgetValsHolder

class AbstractWidgetObjectMixin(ABC):
    @abstractmethod
    def __init__(self, widget_name: str, attrs: AttrHolder = None, values: WidgetValsHolder = None):
        if attrs is None:
            attrs = AttrHolder()
        self._widget_name: str = widget_name
        self._attrs: AttrHolder = attrs
        self._values: WidgetValsHolder = values

    @property
    def widget_name(self) -> str:
        return self._widget_name

    @property
    def attr_list(self) -> List[Attr]:
        return self._attrs.get_attr_list()

    @property
    def values(self) -> WidgetValsHolder:
        return self._values

    @abstractmethod
    def get_relative_geometry(self, format_: GeometryOutputDataFormat) -> 'WidgetGeometry':
        return WidgetGeometryAbsFactory.get_widget_geometry_factory(format_).create_null_widget_geometry()

    def get_attr_state(self, name: AttrName) -> int:
        return self._attrs.get_attr(name).state

    def is_label_input_container(self) -> bool:
        return False


class WidgetObjectMixin(AbstractWidgetObjectMixin, ABC):
    @abstractmethod
    def __init__(self, widget_name: str, widget: QtW.QWidget = None, attrs: AttrHolder = None,
                 vals: WidgetValsHolder = None):
        super(WidgetObjectMixin, self).__init__(widget_name, attrs, vals)
        self._widget = widget

    @property
    def widget(self) -> QtW.QWidget:
        if self._widget is None:
            raise RuntimeError("Qt QWidget of WidgetObject is None. Probably wrong init of WidgetObjectMixin subtype")

        return self._widget

    def get_relative_geometry(self, format_: GeometryOutputDataFormat) -> 'WidgetGeometry':
        widget_enum = WidgetNames.get_enum_by_woclassname(self.__class__.__name__)
        return WidgetGeometryAbsFactory.get_widget_geometry_factory(format_).create_widget_geometry(self._widget,
                                                                                                    widget_enum.padding)


class ContainerWidgetObjectMixin(WidgetObjectMixin, ABC):
    @abstractmethod
    def __init__(self, widget_name: str, widget: QtW.QWidget = None, attrs: AttrHolder = None,
                 vals: WidgetValsHolder = None):
        super(ContainerWidgetObjectMixin, self).__init__(widget_name, widget, attrs, vals)
        self._children: List[WidgetObjectMixin] = []

    @abstractmethod
    def add_child(self, child_widget: WidgetObjectMixin) -> NoReturn:
        self._children.append(child_widget)

    def remove_child(self, widget: WidgetObjectMixin) -> NoReturn:
        self._children.remove(widget)

    def get_child(self, index: int) -> WidgetObjectMixin:
        return self._children[index]

    def get_children(self) -> List[WidgetObjectMixin]:
        return self._children

    def find_descendants(self, wo_type) -> List[WidgetObjectMixin]:
        result = []
        for child in self._children:
            if isinstance(child, wo_type):
                result.append(child)
            if isinstance(child, ContainerWidgetObjectMixin):
                result.extend(child.find_descendants(wo_type))
        return result

    def find_child_index(self, wo_type) -> int:
        for index, child in enumerate(self._children):
            if isinstance(child, wo_type):
                return index
        return -1



class CheckableWidgetObjectMixin(ContainerWidgetObjectMixin, ABC):
    @property
    def checkbox(self):
        return self.get_child(0)

    def init_checkable(self, wo: WidgetObjectMixin):
        self.add_child(wo)
        
    def add_child(self, child_widget: WidgetObjectMixin) -> NoReturn:
        super(CheckableWidgetObjectMixin, self).add_child(child_widget)

class FormItemWidgetObjectMixin(ContainerWidgetObjectMixin, ABC):
    @property
    def widget_child1(self):
        return self.get_child(0)

    @property
    def widget_child2(self):
        return self.get_child(1)

    def init_form_item(self, widget1: WidgetObjectMixin, widget2: WidgetObjectMixin):
        self.add_child(widget1)
        self.add_child(widget2)

    @abstractmethod
    def get_relative_geometry(self, format_: GeometryOutputDataFormat) -> 'WidgetGeometry':
        widget1 = self.widget_child1.widget
        widget2 = self.widget_child2.widget
        widget_enum = WidgetNames.get_enum_by_woclassname(self.__class__.__name__)

        geometry_factory = WidgetGeometryAbsFactory.get_widget_geometry_factory(format_)
        return geometry_factory.create_merged_widget_geometry(widget1, widget2, widget_enum.padding)


class HFormItemWidgetObjectMixin(FormItemWidgetObjectMixin, ABC):
    @property
    def left_widget_object(self) -> WidgetObjectMixin:
        return super().widget_child1

    @property
    def right_widget_object(self) -> WidgetObjectMixin:
        return super().widget_child2

    @abstractmethod
    def get_relative_geometry(self, format_: GeometryOutputDataFormat) -> 'WidgetGeometry':
        return super().get_relative_geometry(format_)


class VFormItemWidgetObjectMixin(FormItemWidgetObjectMixin, ABC):
    @property
    def top_widget_object(self) -> WidgetObjectMixin:
        return super().widget_child1

    @property
    def bottom_widget_object(self) -> WidgetObjectMixin:
        return super().widget_child2

    @abstractmethod
    def get_relative_geometry(self, format_: GeometryOutputDataFormat) -> 'WidgetGeometry':
        return super().get_relative_geometry(format_)


class ScrollableWidgetObjectMixin(ContainerWidgetObjectMixin, ABC):
    def __init__(self, widget_name, widget, attrs: AttrHolder = None, vals: WidgetValsHolder = None):
        if widget is None or isinstance(widget, QtW.QAbstractScrollArea):
            super().__init__(widget_name, widget, attrs, vals)
        else:
            raise RuntimeError("Widget must be QAbstractScrollArea type")

    @property
    def vertical_scroll_bar(self) -> WidgetObjectMixin:
        return self.get_child(0)

    @property
    def horizontal_scroll_bar(self) -> WidgetObjectMixin:
        return self.get_child(1)

    @abstractmethod
    def get_relative_geometry(self, format_: GeometryOutputDataFormat) -> 'WidgetGeometry':
        return super().get_relative_geometry(format_)
