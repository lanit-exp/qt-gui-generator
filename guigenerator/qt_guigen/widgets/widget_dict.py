from typing import Dict, List, Union, Any

from guigenerator.qt_guigen.widgets import GeometryOutputDataFormat
from guigenerator.qt_guigen.widgets.attributes import Attr
from guigenerator.qt_guigen.widgets.widget_geometry import WidgetGeometry
from guigenerator.qt_guigen.widgets.widget_geometry import WidgetGeometryUtils
from guigenerator.qt_guigen.widgets.widget_vals import WidgetContentName
from guigenerator.qt_guigen.widgets.widgetobject.wo_abc import AbstractWidgetObjectMixin, WidgetObjectMixin, \
    ContainerWidgetObjectMixin
# geometry dict: Widget name to Tuple of widget id and WidgetGeometry
# attribute dict: Widget name to Tuple of widget id and Attr
# value dict: Widget name to Tuple of widget id and Dict of WidgetValueName
# and corresponding type
from guigenerator.qt_guigen.widgets.widgetobject.wo_concrete import LabelWidget


class WidgetDataDict:
    def __init__(self, root_widget: 'WidgetObjectMixin'):
        self._geom_dict: Dict[str, Dict[int, WidgetGeometry]] = {}
        self._attr_dict: Dict[str, Dict[int, List[Attr]]] = {}
        self._content_dict: Dict[str, Dict[int, Dict[WidgetContentName, Any]]] = {}
        self._geom_attr_dict: Dict[str, Dict[int, (WidgetGeometry, List[Attr])]] = {}
        self._label_input_link_ids: List['LabelInputIds'] = []

        self._max_width: int = WidgetGeometryUtils.get_relative_widget_frame_geometry(root_widget.widget).width()
        self._max_height: int = WidgetGeometryUtils.get_relative_widget_frame_geometry(root_widget.widget).height()
        self._widget_id = 0

    def get_geometry_items(self):
        return self._geom_dict.items()

    def get_attr_items(self):
        return self._attr_dict.items()

    def get_vals_items(self):
        return self._content_dict.items()

    def get_attr_geometry_items_for_coco(self):
        return self._geom_attr_dict.items()

    def get_label_input_link_ids(self):
        return self._label_input_link_ids

    def add_geometry_attributes_values(self, widget_object: AbstractWidgetObjectMixin, format_: GeometryOutputDataFormat):
        geometry = widget_object.get_relative_geometry(format_)
        if geometry.not_null():
            self.__add_to_dict_geom_item_list(widget_object.widget_name, geometry)
            self.__add_to_dict_item_attr_list(widget_object.widget_name, widget_object.attr_list)
            self.__add_to_dict_item_geom_attr_(widget_object.widget_name, geometry, widget_object.attr_list)
        if widget_object.values is not None:
            self.__add_to_dict_val(widget_object.widget_name, widget_object.values.get_vals_dict())

        self._widget_id += 1

    def get_geometry_distrib(self):
        res = {}
        for name, geometries_dict in self._geom_dict.items():
            res[name] = len(geometries_dict)
        return res


    def __add_to_dict_geom_item_list(self, name_key: str, widget_geometry: WidgetGeometry):
        if name_key not in self._geom_dict.keys():
            self._geom_dict[name_key] = {}
        self._geom_dict[name_key][self._widget_id] = widget_geometry

    def __add_to_dict_item_attr_list(self, name_key: str, attr_list: List[Attr]):
        if name_key not in self._attr_dict.keys():
            self._attr_dict[name_key] = {}
        self._attr_dict[name_key][self._widget_id] = attr_list

    def __add_to_dict_val(self, name_key: str, widget_values: Dict[WidgetContentName, Any]):
        if name_key not in self._content_dict.keys():
            self._content_dict[name_key] = {}
        self._content_dict[name_key][self._widget_id] = widget_values

    def __add_to_dict_item_geom_attr_(self, name_key, geometry, attr_list):
        if name_key not in self._geom_attr_dict.keys():
            self._geom_attr_dict[name_key] = {}
        self._geom_attr_dict[name_key][self._widget_id] = (geometry, attr_list)

    def add_two_last_added_as_label_input_link(self, label_index: int):
        if label_index == 0:
            self._label_input_link_ids.append(
                LabelInputIds(self._widget_id - 2, self._widget_id - 1))
        elif label_index == 1:
            self._label_input_link_ids.append(
                LabelInputIds(self._widget_id - 1, self._widget_id - 2))
        else:
            raise RuntimeError("is_label_input_container "
                               "probably work incorrectly")



class LabelInputIds:
    def __init__(self, label_id: int, input_id: int):
        self.label_id = label_id
        self.input_id = input_id

    def have_id(self, id_):
        return id_ == self.label_id or id_ == self.input_id

    def replace_label_id(self, id_):
        self.label_id = id_

    def replace_input_id(self, id_):
        self.input_id = id_

    def __repr__(self):
        return f"label_id: {self.label_id}  input_id: {self.input_id}"


class WidgetDataDictFactory:
    @classmethod
    def create_dict(cls, root_widget: Union[ContainerWidgetObjectMixin, WidgetObjectMixin],
                    output_data_format: GeometryOutputDataFormat) -> WidgetDataDict:
        dict_ = WidgetDataDict(root_widget)
        cls.__update_dict_with_widget_tree(dict_, root_widget, output_data_format)
        return dict_

    @classmethod
    def create_empty_dict(cls, root_widget: Union[ContainerWidgetObjectMixin, WidgetObjectMixin]):
        return WidgetDataDict(root_widget)

    @classmethod
    def __update_dict_with_widget_tree(cls, dict_: WidgetDataDict,
                                       widget: Union[ContainerWidgetObjectMixin, WidgetObjectMixin],
                                       geom_format: GeometryOutputDataFormat):
        dict_.add_geometry_attributes_values(widget, geom_format)
        if widget.is_label_input_container():
            for child in widget.get_children():
                dict_.add_geometry_attributes_values(child, geom_format)
            label_index = widget.find_child_index(LabelWidget)
            dict_.add_two_last_added_as_label_input_link(label_index)
        elif isinstance(widget, ContainerWidgetObjectMixin):
            for child in widget.get_children():
                cls.__update_dict_with_widget_tree(dict_, child, geom_format)
