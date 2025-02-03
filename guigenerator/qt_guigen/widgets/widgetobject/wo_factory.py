import \
    guigenerator.qt_guigen.widgets.widgetobject.wo_concrete as widget_objects
from guigenerator.dto.tree_dto import TreeDto
from guigenerator.qt_guigen.widgets import MainWindowAccessObject
from guigenerator.qt_guigen.widgets.widget_names import WidgetNames
from guigenerator.qt_guigen.widgets.widgetobject.wo_abc import \
    WidgetObjectMixin, ContainerWidgetObjectMixin


class WidgetObjectFactory:
    @classmethod
    def create_widget_object(cls, description_name: str) -> WidgetObjectMixin:
        class_name = WidgetNames(description_name).woclassname
        return getattr(widget_objects, class_name)(description_name)

    @classmethod
    def create_root_widget_object(cls, description_name: str,
                                  tree: TreeDto) -> ContainerWidgetObjectMixin:
        class_name = WidgetNames(description_name).woclassname
        root_widget = getattr(widget_objects, class_name)(description_name,
                                                          tree)
        MainWindowAccessObject.set_main_window(root_widget.widget)
        return root_widget