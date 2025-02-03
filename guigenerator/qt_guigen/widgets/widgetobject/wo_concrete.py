from abc import ABC
from random import random
from typing import NoReturn, Union, Tuple

from PySide6 import QtWidgets as QtW, QtCore as QtC
from PySide6.QtWidgets import QScrollBar

from guigenerator.dto.tree_dto import TreeDto
from guigenerator.qt_guigen.widgets import GeometryOutputDataFormat, \
    MainWindowAccessObject
from guigenerator.qt_guigen.widgets.attributes import AttrHolderBuilder, \
    AttrHolder, AttrName
from guigenerator.qt_guigen.widgets.qwidgets.qwidgets_factory import \
    QWidgetFactory
from guigenerator.qt_guigen.widgets.widget_geometry import \
    WidgetGeometryAbsFactory, WidgetGeometry
from guigenerator.qt_guigen.widgets.widget_names import WidgetNames
from guigenerator.qt_guigen.widgets.widget_vals import WidgetValsHolder, \
    WidgetValsHolderBuilder
from guigenerator.qt_guigen.widgets.widgetobject.layouts import \
    FlowLayoutObject, GridLayoutObject, LabelGridLayoutObject
from guigenerator.qt_guigen.widgets.widgetobject.wo_abc import \
    ContainerWidgetObjectMixin, WidgetObjectMixin, \
    HFormItemWidgetObjectMixin, VFormItemWidgetObjectMixin, \
    CheckableWidgetObjectMixin, ScrollableWidgetObjectMixin
# container widget objects
# -----------------------------------------------------------------------------
from guigenerator.qt_guigen.widgets.widgetobject.wo_enums import \
    ScrollbarButtonType
from guigenerator.utils import Utils


class MainWindowWidget(ContainerWidgetObjectMixin):
    def __init__(self, widget_name: str, tree: TreeDto, max_row: int = 3,
                 max_col_before_changing_adding_order: int = 3,
                 widget: QtW.QWidget = None, attrs: AttrHolder = None,
                 vals: WidgetValsHolder = None):
        if attrs is None:
            attrs = AttrHolderBuilder().build()
        if vals is None:
            vals = WidgetValsHolderBuilder().build()

        super().__init__(widget_name, widget, attrs, vals)
        self._tree = tree

        if widget is None:
            self._center_widget_layout: GridLayoutObject \
                = GridLayoutObject(tree, max_row,
                                   max_col_before_changing_adding_order)
            # self._center_widget_layout = FlowLayoutObject()
            self._default_widget_init()

    def _default_widget_init(self):
        QWidgetFactory.reset_counters()
        self._widget = QWidgetFactory.create_qwindow(
            self._center_widget_layout.layout, self._tree)
        print(str(Utils.RESOURCES_DIR / 'bg/bg.jpg'))
        self._widget.show()

    def add_child(self, child_widget: WidgetObjectMixin):
        super().add_child(child_widget)

        if isinstance(child_widget, MenuItemWidget):
            self._add_menu_item(child_widget)
        elif isinstance(child_widget, StatusBarWidget):
            self._add_status_bar(child_widget)
        elif isinstance(child_widget, TabWidget):
            self._add_tab_bar(child_widget)
        else:
            self._add_to_central_widget(child_widget)

    def _add_tab_bar(self, tab_bar: 'TabWidget'):
        self._widget.takeCentralWidget()
        self._widget.setCentralWidget(tab_bar.widget)

    def _add_status_bar(self, status_bar: 'StatusBarWidget'):
        self._widget.setStatusBar(status_bar.widget)

    def _add_menu_item(self, menu_item: 'MenuItemWidget'):
        if self._widget.menuBar() is None:
            menu_bar = QtW.QMenuBar()
            self._widget.setMenuWidget(menu_bar)
        self._widget.menuBar().addMenu(menu_item.widget)

    def _add_to_central_widget(self, widget_object: WidgetObjectMixin):
        self._center_widget_layout.add_child(widget_object.widget)

    def clear_menubar(self):
        poses = []
        for pos, child in enumerate(self.get_children()):
            if child.widget_name == "MenuItem":
                poses.append(pos - len(poses))

        for pos in poses:
            self._children.pop(pos)
        self.widget.setMenuWidget(QtW.QMenuBar())


class TabWidget(ContainerWidgetObjectMixin):
    def __init__(self, widget_name: str, widget: QtW.QWidget = None,
                 attrs: AttrHolder = None,
                 vals: WidgetValsHolder = None):
        if attrs is None:
            attrs = AttrHolderBuilder().build()
        if vals is None:
            vals = WidgetValsHolderBuilder().build()

        super().__init__(widget_name, widget, attrs, vals)
        if widget is None:
            self._default_widget_init()

    def _default_widget_init(self):
        main_window: QtW.QMainWindow = MainWindowAccessObject.get_main_window()
        self._widget = QWidgetFactory.create_qtabwidget(
            main_window.centralWidget())

        tab_bar = self._widget.tabBar()
        for tab_index in range(tab_bar.count()):
            tab_button_name = WidgetNames.get_description_name(
                TabButtonWidget.__name__)
            tab_button = TabButtonWidget(tab_button_name,
                                         tab_rect=tab_bar.tabRect(tab_index))
            self.add_child(tab_button)

    def add_child(self, widget_object: WidgetObjectMixin) -> NoReturn:
        super().add_child(widget_object)

    def get_relative_geometry(self,
                              format_: GeometryOutputDataFormat) -> \
            'WidgetGeometry':
        return WidgetGeometryAbsFactory.get_widget_geometry_factory(
            format_).create_null_widget_geometry()


class FormBoxContainerWidget(ContainerWidgetObjectMixin):
    def __init__(self, widget_name: str, widget: QtW.QWidget = None,
                 attrs: AttrHolder = None,
                 vals: WidgetValsHolder = None):
        if attrs is None:
            attrs = AttrHolderBuilder().build()
        if vals is None:
            vals = WidgetValsHolderBuilder().build()
        super().__init__(widget_name, widget, attrs, vals)
        if widget is None:
            self._default_widget_init()

    def _default_widget_init(self):
        self._widget = QtW.QWidget()
        self._layout = QtW.QFormLayout()
        self._widget.setLayout(self._layout)

    def add_child(self, widget_object: Union[WidgetObjectMixin,
                                             HFormItemWidgetObjectMixin]):
        super().add_child(widget_object)

        if isinstance(widget_object, HFormItemWidgetObjectMixin):
            self._add_hform_box_item(widget_object)
        elif isinstance(widget_object, VFormItemWidgetObjectMixin):
            self._add_vform_box_item(widget_object)
        elif isinstance(widget_object, WidgetObjectMixin):
            self._add_widget(widget_object)

    def _add_widget(self, widget_object: WidgetObjectMixin):
        self._layout.addRow(widget_object.widget)

    def _add_hform_box_item(self, widget_object: HFormItemWidgetObjectMixin):
        self._layout.addRow(widget_object.left_widget_object.widget,
                            widget_object.right_widget_object.widget)

    def _add_vform_box_item(self, widget_object: VFormItemWidgetObjectMixin):
        self._layout.addRow(widget_object.top_widget_object.widget)
        self._layout.addRow(widget_object.bottom_widget_object.widget)


class GroupBoxContainerWidget(ContainerWidgetObjectMixin):
    def __init__(self, widget_name: str, widget: QtW.QWidget = None,
                 attrs: AttrHolder = None,
                 vals: WidgetValsHolder = None):
        if vals is None:
            vals = WidgetValsHolderBuilder().build()
        if attrs is None:
            attrs = AttrHolderBuilder().build()
        super().__init__(widget_name, widget, attrs, vals)
        if widget is None:
            self._default_widget_init()

    def _default_widget_init(self):
        self._widget = QWidgetFactory.create_qgroupbox()
        self._widget.setLayout(QtW.QHBoxLayout())

    def add_child(self, widget_object: Union[WidgetObjectMixin,
                                             HFormItemWidgetObjectMixin]):
        super().add_child(widget_object)
        self._widget.layout().addWidget(widget_object.widget)


# composite widgets
# ----------------------------------------------------------------------------------------------------
class LabeledCheckBoxHFormItemWidget(HFormItemWidgetObjectMixin):
    def __init__(self, widget_name: str, widget: QtW.QWidget = None,
                 attrs: AttrHolder = None,
                 vals: WidgetValsHolder = None):
        if attrs is None:
            attrs = AttrHolderBuilder().build()
        if vals is None:
            vals = WidgetValsHolderBuilder().build()
        super().__init__(widget_name, widget, attrs, vals)
        if widget is None:
            self._default_widget_init()

    def _default_widget_init(self):
        label, checkbox = QWidgetFactory.create_labeled_qcheckbox()
        label_name = WidgetNames.get_description_name(LabelWidget.__name__)
        checkbox_name = WidgetNames.get_description_name(
            CheckBoxWidget.__name__)
        self.init_form_item(CheckBoxWidget(checkbox_name, checkbox),
                            LabelWidget(label_name, label))
        self._widget = checkbox

    def add_child(self, child_widget: WidgetObjectMixin) -> NoReturn:
        super().add_child(child_widget)

    def get_relative_geometry(self,
                              format_: GeometryOutputDataFormat) -> \
            'WidgetGeometry':
        return super().get_relative_geometry(format_)


class RevLabeledCheckBoxHFormItemWidget(HFormItemWidgetObjectMixin):
    def __init__(self, widget_name: str, widget: QtW.QWidget = None,
                 attrs: AttrHolder = None,
                 vals: WidgetValsHolder = None):
        if attrs is None:
            attrs = AttrHolderBuilder().build()
        if vals is None:
            vals = WidgetValsHolderBuilder().build()
        super().__init__(widget_name, widget, attrs, vals)
        if widget is None:
            self._default_widget_init()

    def _default_widget_init(self):
        label, checkbox = QWidgetFactory.create_labeled_qcheckbox()
        label_name = WidgetNames.get_description_name(LabelWidget.__name__)
        checkbox_name = WidgetNames.get_description_name(
            CheckBoxWidget.__name__)
        self.init_form_item(LabelWidget(label_name, label),
                            CheckBoxWidget(checkbox_name, checkbox), )
        self._widget = checkbox

    def add_child(self, child_widget: WidgetObjectMixin) -> NoReturn:
        super().add_child(child_widget)

    def get_relative_geometry(self,
                              format_: GeometryOutputDataFormat) -> \
            'WidgetGeometry':
        return super().get_relative_geometry(format_)


class TopLabeledCheckBoxVFormItemWidget(VFormItemWidgetObjectMixin):
    def __init__(self, widget_name: str, widget: QtW.QTableWidget = None,
                 attrs: AttrHolder = None,
                 vals: WidgetValsHolder = None):
        if attrs is None:
            attrs = AttrHolderBuilder().build()
        if vals is None:
            vals = WidgetValsHolderBuilder().build()
        super().__init__(widget_name, widget, attrs, vals)
        if widget is None:
            self._default_widget_init()

    def _default_widget_init(self):
        label, checkbox = QWidgetFactory.create_labeled_qcheckbox()
        label_name = WidgetNames.get_description_name(LabelWidget.__name__)
        checkbox_name = WidgetNames.get_description_name(
            CheckBoxWidget.__name__)
        self.init_form_item(LabelWidget(label_name, label),
                            CheckBoxWidget(checkbox_name, checkbox))
        self._widget = checkbox

    def get_relative_geometry(self,
                              format_: GeometryOutputDataFormat) -> \
            'WidgetGeometry':
        return super().get_relative_geometry(format_)

    def add_child(self, child_widget: WidgetObjectMixin) -> NoReturn:
        super().add_child(child_widget)


class LabeledRadioButtonHFormItemWidget(HFormItemWidgetObjectMixin):
    def __init__(self, widget_name: str, widget: QtW.QWidget = None,
                 attrs: AttrHolder = None,
                 vals: WidgetValsHolder = None):
        if attrs is None:
            attrs = AttrHolderBuilder().build()
        if vals is None:
            vals = WidgetValsHolderBuilder().build()
        super().__init__(widget_name, widget, attrs, vals)
        if widget is None:
            self._default_widget_init()

    def _default_widget_init(self):
        label, radiobutton = QWidgetFactory.create_labeled_qradiobutton()
        label_name = WidgetNames.get_description_name(LabelWidget.__name__)
        radio_name = WidgetNames.get_description_name(
            RadioButtonWidget.__name__)
        self.init_form_item(RadioButtonWidget(radio_name, radiobutton),
                            LabelWidget(label_name, label))
        self._widget = radiobutton

    def add_child(self, child_widget: WidgetObjectMixin) -> NoReturn:
        super().add_child(child_widget)

    def get_relative_geometry(self,
                              format_: GeometryOutputDataFormat) -> \
            'WidgetGeometry':
        return super().get_relative_geometry(format_)


class RevLabeledRadioButtonHFormItemWidget(HFormItemWidgetObjectMixin):
    def __init__(self, widget_name: str, widget: QtW.QWidget = None,
                 attrs: AttrHolder = None,
                 vals: WidgetValsHolder = None):
        if attrs is None:
            attrs = AttrHolderBuilder().build()
        if vals is None:
            vals = WidgetValsHolderBuilder().build()
        super().__init__(widget_name, widget, attrs, vals)
        if widget is None:
            self._default_widget_init()

    def _default_widget_init(self):
        label, radiobutton = QWidgetFactory.create_labeled_qradiobutton()
        label_name = WidgetNames.get_description_name(LabelWidget.__name__)
        radio_name = WidgetNames.get_description_name(
            RadioButtonWidget.__name__)
        self.init_form_item(LabelWidget(label_name, label),
                            RadioButtonWidget(radio_name, radiobutton))
        self._widget = radiobutton

    def add_child(self, child_widget: WidgetObjectMixin) -> NoReturn:
        super().add_child(child_widget)

    def get_relative_geometry(self,
                              format_: GeometryOutputDataFormat) -> \
            'WidgetGeometry':
        return super().get_relative_geometry(format_)


class TopLabeledRadioButtonVFormItemWidget(VFormItemWidgetObjectMixin):
    def __init__(self, widget_name: str, widget: QtW.QWidget = None,
                 attrs: AttrHolder = None,
                 vals: WidgetValsHolder = None):
        if attrs is None:
            attrs = AttrHolderBuilder().build()
        if vals is None:
            vals = WidgetValsHolderBuilder().build()
        super().__init__(widget_name, widget, attrs, vals)
        if widget is None:
            self._default_widget_init()

    def _default_widget_init(self):
        label, radiobutton = QWidgetFactory.create_labeled_qradiobutton()
        label_name = WidgetNames.get_description_name(LabelWidget.__name__)
        radio_name = WidgetNames.get_description_name(
            RadioButtonWidget.__name__)
        self.init_form_item(LabelWidget(label_name, label),
                            RadioButtonWidget(radio_name, radiobutton))
        self._widget = radiobutton

    def add_child(self, child_widget: WidgetObjectMixin) -> NoReturn:
        super().add_child(child_widget)

    def get_relative_geometry(self,
                              format_: GeometryOutputDataFormat) -> \
            'WidgetGeometry':
        return super().get_relative_geometry(format_)


class LabeledInputHFormItemWidget(HFormItemWidgetObjectMixin):
    def __init__(self, widget_name: str, widget: QtW.QWidget = None,
                 attrs: AttrHolder = None,
                 vals: WidgetValsHolder = None):
        if attrs is None:
            attrs = AttrHolderBuilder().build()
        if vals is None:
            vals = WidgetValsHolderBuilder().build()
        super().__init__(widget_name, widget, attrs, vals)
        if widget is None:
            self._default_widget_init()

    def _default_widget_init(self):
        label_name = WidgetNames.get_description_name(LabelWidget.__name__)
        input_name = WidgetNames.get_description_name(InputWidget.__name__)
        label = LabelWidget(label_name,  words_count_range=(1, 3))
        self.init_form_item(label, InputWidget(input_name))

    def add_child(self, child_widget: WidgetObjectMixin) -> NoReturn:
        super().add_child(child_widget)

    def get_relative_geometry(self,
                              format_: GeometryOutputDataFormat) -> \
            'WidgetGeometry':
        return super().get_relative_geometry(format_)

    def is_label_input_container(self) -> bool:
        return True


class RevInputEditHFormItemWidget(HFormItemWidgetObjectMixin):
    def __init__(self, widget_name: str, widget: QtW.QWidget = None,
                 attrs: AttrHolder = None,
                 vals: WidgetValsHolder = None):
        if attrs is None:
            attrs = AttrHolderBuilder().build()
        if vals is None:
            vals = WidgetValsHolderBuilder().build()
        super().__init__(widget_name, widget, attrs, vals)
        if widget is None:
            self._default_widget_init()

    def _default_widget_init(self):
        label_name = WidgetNames.get_description_name(LabelWidget.__name__)
        input_name = WidgetNames.get_description_name(InputWidget.__name__)
        label = LabelWidget(label_name, words_count_range=(1, 3))
        self.init_form_item(InputWidget(input_name), label)

    def add_child(self, child_widget: WidgetObjectMixin) -> NoReturn:
        super().add_child(child_widget)

    def get_relative_geometry(self,
                              format_: GeometryOutputDataFormat) -> \
            'WidgetGeometry':
        return super().get_relative_geometry(format_)

    def is_label_input_container(self) -> bool:
        return True


class TopLabeledInputVFormItemWidget(VFormItemWidgetObjectMixin):
    def __init__(self, widget_name: str, widget: QtW.QWidget = None,
                 attrs: AttrHolder = None,
                 vals: WidgetValsHolder = None):
        if attrs is None:
            attrs = AttrHolderBuilder().build()
        if vals is None:
            vals = WidgetValsHolderBuilder().build()
        super().__init__(widget_name, widget, attrs, vals)
        if widget is None:
            self._default_widget_init()

    def _default_widget_init(self):
        label_name = WidgetNames.get_description_name(LabelWidget.__name__)
        label = LabelWidget(label_name, words_count_range=(1, 3))
        input_name = WidgetNames.get_description_name(InputWidget.__name__)
        input_ = InputWidget(input_name)
        self.init_form_item(label, input_)

    def add_child(self, child_widget: WidgetObjectMixin) -> NoReturn:
        super().add_child(child_widget)

    def get_relative_geometry(self,
                              format_: GeometryOutputDataFormat) -> \
            'WidgetGeometry':
        return super().get_relative_geometry(format_)

    def is_label_input_container(self) -> bool:
        return True


class LabeledLineEditHFormItemWidget(HFormItemWidgetObjectMixin):
    def __init__(self, widget_name: str, widget: QtW.QWidget = None,
                 attrs: AttrHolder = None,
                 vals: WidgetValsHolder = None):
        if attrs is None:
            attrs = AttrHolderBuilder().build()
        if vals is None:
            vals = WidgetValsHolderBuilder().build()
        super().__init__(widget_name, widget, attrs, vals)
        if widget is None:
            self._default_widget_init()

    def _default_widget_init(self):
        label_name = WidgetNames.get_description_name(LabelWidget.__name__)
        edit_name = WidgetNames.get_description_name(LineEditWidget.__name__)
        self.init_form_item(LabelWidget(label_name,  words_count_range=(2, 3)),
                            LineEditWidget(edit_name))

    def add_child(self, child_widget: WidgetObjectMixin) -> NoReturn:
        super().add_child(child_widget)

    def get_relative_geometry(self,
                              format_: GeometryOutputDataFormat) -> \
            'WidgetGeometry':
        return super().get_relative_geometry(format_)


class RevLabeledLineEditHFormItemWidget(HFormItemWidgetObjectMixin):
    def __init__(self, widget_name: str, widget: QtW.QWidget = None,
                 attrs: AttrHolder = None,
                 vals: WidgetValsHolder = None):
        if attrs is None:
            attrs = AttrHolderBuilder().build()
        if vals is None:
            vals = WidgetValsHolderBuilder().build()
        super().__init__(widget_name, widget, attrs, vals)
        if widget is None:
            self._default_widget_init()

    def _default_widget_init(self):
        label_name = WidgetNames.get_description_name(LabelWidget.__name__)
        edit_name = WidgetNames.get_description_name(LineEditWidget.__name__)
        self.init_form_item(LabelWidget(label_name,  words_count_range=(2, 3)),
                            LineEditWidget(edit_name), )

    def add_child(self, child_widget: WidgetObjectMixin) -> NoReturn:
        super().add_child(child_widget)

    def get_relative_geometry(self,
                              format_: GeometryOutputDataFormat) -> \
            'WidgetGeometry':
        return super().get_relative_geometry(format_)


class TopLabeledLineEditVFormItemWidget(VFormItemWidgetObjectMixin):
    def __init__(self, widget_name: str, widget: QtW.QWidget = None,
                 attrs: AttrHolder = None,
                 vals: WidgetValsHolder = None):
        if attrs is None:
            attrs = AttrHolderBuilder().build()
        if vals is None:
            vals = WidgetValsHolderBuilder().build()
        super().__init__(widget_name, widget, attrs, vals)
        if widget is None:
            self._default_widget_init()

    def _default_widget_init(self):
        label_name = WidgetNames.get_description_name(LabelWidget.__name__)
        label = LabelWidget(label_name)
        edit_name = WidgetNames.get_description_name(LineEditWidget.__name__)
        edit = LineEditWidget(edit_name)
        self.init_form_item(label, edit)

    def add_child(self, child_widget: WidgetObjectMixin) -> NoReturn:
        super().add_child(child_widget)

    def get_relative_geometry(self,
                              format_: GeometryOutputDataFormat) -> \
            'WidgetGeometry':
        return super().get_relative_geometry(format_)


class LabeledCheckableLineEditHFormItemWidget(HFormItemWidgetObjectMixin):
    def __init__(self, widget_name: str, widget: QtW.QWidget = None,
                 attrs: AttrHolder = None,
                 vals: WidgetValsHolder = None):
        if attrs is None:
            attrs = AttrHolderBuilder().build()
        if vals is None:
            vals = WidgetValsHolderBuilder().build()
        super().__init__(widget_name, widget, attrs, vals)
        if widget is None:
            self._default_widget_init()

    def _default_widget_init(self):
        label_name = WidgetNames.get_description_name(LabelWidget.__name__)
        ch_edit_name = WidgetNames.get_description_name(
            CheckableLineEditWidget.__name__)
        self.init_form_item(LabelWidget(label_name),
                            CheckableLineEditWidget(ch_edit_name))

    def add_child(self, child_widget: WidgetObjectMixin) -> NoReturn:
        super().add_child(child_widget)

    def get_relative_geometry(self,
                              format_: GeometryOutputDataFormat) -> \
            'WidgetGeometry':
        return super().get_relative_geometry(format_)


class RevLabeledCheckableLineEditHFormItemWidget(HFormItemWidgetObjectMixin):
    def __init__(self, widget_name: str, widget: QtW.QWidget = None,
                 attrs: AttrHolder = None,
                 vals: WidgetValsHolder = None):
        if attrs is None:
            attrs = AttrHolderBuilder().build()
        if vals is None:
            vals = WidgetValsHolderBuilder().build()
        super().__init__(widget_name, widget, attrs, vals)
        if widget is None:
            self._default_widget_init()

    def _default_widget_init(self):
        label_name = WidgetNames.get_description_name(LabelWidget.__name__)
        ch_edit_name = WidgetNames.get_description_name(
            CheckableLineEditWidget.__name__)
        self.init_form_item(CheckableLineEditWidget(ch_edit_name),
                            LabelWidget(label_name))

    def add_child(self, child_widget: WidgetObjectMixin) -> NoReturn:
        super().add_child(child_widget)

    def get_relative_geometry(self,
                              format_: GeometryOutputDataFormat) -> \
            'WidgetGeometry':
        return super().get_relative_geometry(format_)


class TopLabeledCheckableLineEditVFormItemWidget(VFormItemWidgetObjectMixin):
    def __init__(self, widget_name: str, widget: QtW.QWidget = None,
                 attrs: AttrHolder = None,
                 vals: WidgetValsHolder = None):
        if attrs is None:
            attrs = AttrHolderBuilder().build()
        if vals is None:
            vals = WidgetValsHolderBuilder().build()
        super().__init__(widget_name, widget, attrs, vals)
        if widget is None:
            self._default_widget_init()

    def _default_widget_init(self):
        label_name = WidgetNames.get_description_name(LabelWidget.__name__)
        label = LabelWidget(label_name)
        edit_name = WidgetNames.get_description_name(
            CheckableLineEditWidget.__name__)
        ch_edit = CheckableLineEditWidget(edit_name)
        self.init_form_item(label, ch_edit)

    def add_child(self, child_widget: WidgetObjectMixin) -> NoReturn:
        super().add_child(child_widget)

    def get_relative_geometry(self,
                              format_: GeometryOutputDataFormat) -> \
            'WidgetGeometry':
        return super().get_relative_geometry(format_)


class LabeledComboBoxHFormItemWidget(HFormItemWidgetObjectMixin):
    def __init__(self, widget_name: str, widget: QtW.QWidget = None,
                 attrs: AttrHolder = None,
                 vals: WidgetValsHolder = None):
        if attrs is None:
            attrs = AttrHolderBuilder().build()
        if vals is None:
            vals = WidgetValsHolderBuilder().build()
        super().__init__(widget_name, widget, attrs, vals)
        if widget is None:
            self._default_widget_init()

    def _default_widget_init(self):
        label_name = WidgetNames.get_description_name(LabelWidget.__name__)
        combobox_name = WidgetNames.get_description_name(
            ComboBoxWidget.__name__)
        self.init_form_item(LabelWidget(label_name),
                            ComboBoxWidget(combobox_name))

    def add_child(self, child_widget: WidgetObjectMixin) -> NoReturn:
        super().add_child(child_widget)

    def get_relative_geometry(self,
                              format_: GeometryOutputDataFormat) -> \
            'WidgetGeometry':
        return super().get_relative_geometry(format_)


class LabeledCheckableComboBoxHFormItemWidget(HFormItemWidgetObjectMixin):
    def __init__(self, widget_name: str, widget: QtW.QWidget = None,
                 attrs: AttrHolder = None,
                 vals: WidgetValsHolder = None):
        if attrs is None:
            attrs = AttrHolderBuilder().build()
        if vals is None:
            vals = WidgetValsHolderBuilder().build()
        super().__init__(widget_name, widget, attrs, vals)
        if widget is None:
            self._default_widget_init()

    def _default_widget_init(self):
        label_name = WidgetNames.get_description_name(LabelWidget.__name__)
        combobox_name = WidgetNames.get_description_name(
            CheckableComboBoxWidget.__name__)
        self.init_form_item(LabelWidget(label_name),
                            CheckableComboBoxWidget(combobox_name))

    def add_child(self, child_widget: WidgetObjectMixin) -> NoReturn:
        super().add_child(child_widget)

    def get_relative_geometry(self,
                              format_: GeometryOutputDataFormat) -> \
            'WidgetGeometry':
        return super().get_relative_geometry(format_)


class RevLabeledComboBoxHFormItemWidget(HFormItemWidgetObjectMixin):
    def __init__(self, widget_name: str, widget: QtW.QWidget = None,
                 attrs: AttrHolder = None,
                 vals: WidgetValsHolder = None):
        if attrs is None:
            attrs = AttrHolderBuilder().build()
        if vals is None:
            vals = WidgetValsHolderBuilder().build()
        super().__init__(widget_name, widget, attrs, vals)
        if widget is None:
            self._default_widget_init()

    def _default_widget_init(self):
        label_name = WidgetNames.get_description_name(LabelWidget.__name__)
        combobox_name = WidgetNames.get_description_name(
            ComboBoxWidget.__name__)
        self.init_form_item(ComboBoxWidget(combobox_name),
                            LabelWidget(label_name))

    def add_child(self, child_widget: WidgetObjectMixin) -> NoReturn:
        super().add_child(child_widget)

    def get_relative_geometry(self,
                              format_: GeometryOutputDataFormat) -> \
            'WidgetGeometry':
        return super().get_relative_geometry(format_)


class RevLabeledCheckableComboBoxHFormItemWidget(HFormItemWidgetObjectMixin):
    def __init__(self, widget_name: str, widget: QtW.QWidget = None,
                 attrs: AttrHolder = None,
                 vals: WidgetValsHolder = None):
        if attrs is None:
            attrs = AttrHolderBuilder().build()
        if vals is None:
            vals = WidgetValsHolderBuilder().build()
        super().__init__(widget_name, widget, attrs, vals)
        if widget is None:
            self._default_widget_init()

    def _default_widget_init(self):
        label_name = WidgetNames.get_description_name(LabelWidget.__name__)
        combobox_name = WidgetNames.get_description_name(
            CheckableComboBoxWidget.__name__)
        self.init_form_item(CheckableComboBoxWidget(combobox_name),
                            LabelWidget(label_name))

    def add_child(self, child_widget: WidgetObjectMixin) -> NoReturn:
        super().add_child(child_widget)

    def get_relative_geometry(self,
                              format_: GeometryOutputDataFormat) -> \
            'WidgetGeometry':
        return super().get_relative_geometry(format_)


class TopLabeledComboBoxVFormItemWidget(VFormItemWidgetObjectMixin):
    def __init__(self, widget_name: str, widget: QtW.QWidget = None,
                 attrs: AttrHolder = None,
                 vals: WidgetValsHolder = None):
        if attrs is None:
            attrs = AttrHolderBuilder().build()
        if vals is None:
            vals = WidgetValsHolderBuilder().build()
        super().__init__(widget_name, widget, attrs, vals)
        if widget is None:
            self._default_widget_init()

    def _default_widget_init(self):
        label_name = WidgetNames.get_description_name(LabelWidget.__name__)
        combobox_name = WidgetNames.get_description_name(
            ComboBoxWidget.__name__)
        self.init_form_item(LabelWidget(label_name),
                            ComboBoxWidget(combobox_name))

    def add_child(self, child_widget: WidgetObjectMixin) -> NoReturn:
        super().add_child(child_widget)

    def get_relative_geometry(self,
                              format_: GeometryOutputDataFormat) -> \
            'WidgetGeometry':
        return super().get_relative_geometry(format_)


class TopLabeledCheckableComboBoxVFormItemWidget(VFormItemWidgetObjectMixin):
    def __init__(self, widget_name: str, widget: QtW.QWidget = None,
                 attrs: AttrHolder = None,
                 vals: WidgetValsHolder = None):
        if attrs is None:
            attrs = AttrHolderBuilder().build()
        if vals is None:
            vals = WidgetValsHolderBuilder().build()
        super().__init__(widget_name, widget, attrs, vals)
        if widget is None:
            self._default_widget_init()

    def _default_widget_init(self):
        label_name = WidgetNames.get_description_name(LabelWidget.__name__)
        combobox_name = WidgetNames.get_description_name(
            CheckableComboBoxWidget.__name__)
        self.init_form_item(LabelWidget(label_name),
                            CheckableComboBoxWidget(combobox_name), )

    def add_child(self, child_widget: WidgetObjectMixin) -> NoReturn:
        super().add_child(child_widget)

    def get_relative_geometry(self,
                              format_: GeometryOutputDataFormat) -> \
            'WidgetGeometry':
        return super().get_relative_geometry(format_)


# leaves widget objects
# ------------------------------------------------------------------------------------------------

class MenuItemWidget(WidgetObjectMixin):
    n_menu_item = 0

    def __init__(self, widget_name: str, widget: QtW.QWidget = None,
                 attrs: AttrHolder = None,
                 vals: WidgetValsHolder = None):
        super().__init__(widget_name, widget, attrs, vals)
        self._id = self._get_id()

        if widget is None:
            self._default_widget_init()

    @classmethod
    def _get_id(cls) -> int:
        current_id = cls.n_menu_item
        cls.n_menu_item += 1
        return current_id

    @property
    def id(self) -> int:
        return self._id

    def _default_widget_init(self):
        self._widget = QWidgetFactory.create_qmenu()

    def get_relative_geometry(self,
                              format_: GeometryOutputDataFormat) -> \
            'WidgetGeometry':
        widget_enum = WidgetNames.get_enum_by_woclassname(
            self.__class__.__name__)
        return WidgetGeometryAbsFactory.get_widget_geometry_factory(format_) \
            .create_menu_widget_geometry(self._id, widget_enum.padding,
                                         self.widget)

    @classmethod
    def reset_id_count(cls):
        cls.n_menu_item = 0


class StatusBarWidget(WidgetObjectMixin):
    def __init__(self, widget_name: str, widget: QtW.QWidget = None,
                 attrs: AttrHolder = None,
                 vals: WidgetValsHolder = None):
        super().__init__(widget_name, widget, attrs, vals)
        if widget is None:
            self._default_widget_init()

    def _default_widget_init(self):
        self._widget = QWidgetFactory.create_qstatusbar()


class TabButtonWidget(WidgetObjectMixin):
    def __init__(self, widget_name: str, widget: QtW.QWidget = None,
                 tab_rect: QtC.QRect = None):
        super().__init__(widget_name, widget)
        self.tab_rect = tab_rect

    def get_relative_geometry(self,
                              format_: GeometryOutputDataFormat) -> \
            'WidgetGeometry':
        widget_enum = WidgetNames.get_enum_by_woclassname(
            self.__class__.__name__)
        if self.tab_rect is None:
            raise RuntimeError(
                "Cant create TabButton geometry. QRect is not assigned")
        return WidgetGeometryAbsFactory.get_widget_geometry_factory(
            format_).create_tab_button_geometry(
            widget_enum.padding,
            self.tab_rect)


class ButtonWidget(WidgetObjectMixin):
    def __init__(self, widget_name: str, widget: QtW.QWidget = None,
                 attrs: AttrHolder = None,
                 vals: WidgetValsHolder = None):
        super().__init__(widget_name, widget, attrs, vals)
        if widget is None:
            self._default_widget_init()
        if attrs is None:
            self._default_attrs_init()
        if vals is None:
            self._default_vals_init()

    def _default_widget_init(self):
        b = QWidgetFactory.create_qbutton()
        self._widget = b

    def _default_attrs_init(self):
        b = self._widget
        has_text_ = b.text() != ''
        iconed_ = not b.icon().isNull()
        self._attrs = AttrHolderBuilder().enableable(b.isEnabled()).has_text(
            has_text_).iconed(iconed_).build()

    def _default_vals_init(self):
        b = self._widget
        text_ = '"' + b.text() + '"'
        self._values = WidgetValsHolderBuilder().text(text_).build()


class LineEditWidget(WidgetObjectMixin):
    def __init__(self, widget_name: str, widget: QtW.QWidget = None,
                 attrs: AttrHolder = None,
                 vals: WidgetValsHolder = None):
        super().__init__(widget_name, widget, attrs, vals)
        if widget is None:
            self._default_widget_init()
        if attrs is None:
            self._default_attrs_init()
        if vals is None:
            self._default_vals_init()

    def _default_widget_init(self):
        edit = QWidgetFactory.create_qline_edit()
        self._widget = edit

    def _default_attrs_init(self):
        e = self._widget
        has_text = e.text() != ''
        self._attrs = AttrHolderBuilder().enableable(e.isEnabled()).has_text(
            has_text).build()

    def _default_vals_init(self):
        e = self._widget
        text_ = '"' + e.text() + '"'
        self._values = WidgetValsHolderBuilder().text(text_).build()


class InputWidget(ContainerWidgetObjectMixin):
    def __init__(self, widget_name: str, widget: QtW.QWidget = None,
                 attrs: AttrHolder = None,
                 vals: WidgetValsHolder = None):
        if attrs is None:
            attrs = AttrHolderBuilder().build()
        if vals is None:
            vals = WidgetValsHolderBuilder().build()
        super().__init__(widget_name, widget, attrs, vals)
        if widget is None:
            self._default_widget_init()

    def _default_widget_init(self):
        attr_holder_builder = AttrHolderBuilder()
        if random() < 0.5:
            attr_holder_builder.type(1)
            if random() < 0.5:
                name = WidgetNames.get_description_name(
                    ComboBoxWidget.__name__)
                widget_proxy = ComboBoxWidget(name)
            else:
                name = WidgetNames.get_description_name(
                    CheckableComboBoxWidget.__name__)
                widget_proxy = CheckableComboBoxWidget(name)
                attr_holder_builder.checkable(widget_proxy.get_attr_state(
                    AttrName.CHECKABLE))
        else:
            attr_holder_builder.type(0)
            if random() < 0.5:
                name = WidgetNames.get_description_name(
                    LineEditWidget.__name__)
                widget_proxy = LineEditWidget(name)
            else:
                name = WidgetNames.get_description_name(
                    CheckableLineEditWidget.__name__)
                widget_proxy = CheckableLineEditWidget(name)
                attr_holder_builder.checkable(
                    widget_proxy.get_attr_state(AttrName.CHECKABLE))

        attr_holder_builder.enableable(
            widget_proxy.get_attr_state(AttrName.ENABLEABLE)) \
            .has_text(widget_proxy.get_attr_state(AttrName.HAS_TEXT))
        self._attrs = attr_holder_builder.build()
        self._widget = widget_proxy.widget
        self.add_child(widget_proxy)

    def add_child(self, widget_object: Union[WidgetObjectMixin,
                                             HFormItemWidgetObjectMixin]):
        super().add_child(widget_object)

    def get_relative_geometry(self,
                              format_: GeometryOutputDataFormat) -> \
            'WidgetGeometry':
        widget_enum = WidgetNames.get_enum_by_woclassname(
            self.__class__.__name__)
        return WidgetGeometryAbsFactory \
            .get_widget_geometry_factory(format_) \
            .create_widget_geometry(self._widget, widget_enum.padding)


class CheckableLineEditWidget(CheckableWidgetObjectMixin):
    def __init__(self, widget_name: str, widget: QtW.QWidget = None,
                 attrs: AttrHolder = None,
                 vals: WidgetValsHolder = None):
        super().__init__(widget_name, widget, attrs, vals)
        if widget is None:
            self._default_widget_init()

    def _default_widget_init(self):
        ch_edit = QWidgetFactory.create_qcheckable_line_edit()
        has_text = ch_edit.text() != ''
        self._widget = ch_edit
        self._attrs = AttrHolderBuilder().enableable(
            ch_edit.isEnabled()).has_text(has_text) \
            .checkable(ch_edit.checkbox.isChecked()).build()
        checkbox_name = WidgetNames.get_description_name(
            CheckBoxWidget.__name__)
        self.init_checkable(CheckBoxWidget(checkbox_name, ch_edit.checkbox))

    def add_child(self, child_widget: WidgetObjectMixin) -> NoReturn:
        super().add_child(child_widget)

    def get_relative_geometry(self,
                              format_: GeometryOutputDataFormat) -> \
            'WidgetGeometry':
        return super(CheckableLineEditWidget, self).get_relative_geometry(
            format_)


class ComboBoxWidget(WidgetObjectMixin):
    def __init__(self, widget_name: str, widget: QtW.QWidget = None,
                 attrs: AttrHolder = None,
                 vals: WidgetValsHolder = None):
        super().__init__(widget_name, widget, attrs, vals)
        if widget is None:
            self._default_widget_init()
        if attrs is None:
            self._default_attrs_init()
        if vals is None:
            self._default_vals_init()

    def _default_widget_init(self):
        cb = QWidgetFactory.create_qcombobox()
        self._widget = cb

    def _default_attrs_init(self):
        cb = self._widget
        has_text = cb.currentText() != ''
        self._attrs = AttrHolderBuilder() \
            .enableable(cb.isEnabled()) \
            .has_text(has_text) \
            .build()

    def _default_vals_init(self):
        cb = self._widget
        text_ = '"' + cb.currentText() + '"'
        self._values = WidgetValsHolderBuilder().text(text_).build()


class CheckableComboBoxWidget(CheckableWidgetObjectMixin):
    def __init__(self, widget_name: str, widget: QtW.QWidget = None,
                 attrs: AttrHolder = None,
                 vals: WidgetValsHolder = None):
        super().__init__(widget_name, widget, attrs, vals)
        if widget is None:
            self._default_widget_init()
        if attrs is None:
            self.__default_attrs_init()

    def _default_widget_init(self):
        cb = QWidgetFactory.create_qcheckable_combobox()
        self._widget = cb
        checkbox_name = WidgetNames.get_description_name(
            CheckBoxWidget.__name__)
        self.init_checkable(CheckBoxWidget(checkbox_name, cb.checkbox))

    def add_child(self, child_widget: WidgetObjectMixin) -> NoReturn:
        super().add_child(child_widget)

    def __default_attrs_init(self):
        cb = self._widget
        has_text = cb.currentText() != ''
        self._attrs = AttrHolderBuilder() \
            .enableable(cb.isEnabled()) \
            .has_text(has_text) \
            .checkable(cb.checkbox.isChecked()) \
            .build()


class ScrollableWidgetObject(ScrollableWidgetObjectMixin, ABC):
    def __init__(self, widget_name: str, widget: QtW.QWidget = None,
                 attrs: AttrHolder = None,
                 vals: WidgetValsHolder = None):
        super().__init__(widget_name, widget, attrs, vals)

    def _default_attrs_init(self):
        scrollable = self._widget
        self._attrs = AttrHolderBuilder() \
            .enableable(scrollable.isEnabled()) \
            .vscrollable(scrollable.verticalScrollBar().isVisible()) \
            .hscrollable(scrollable.horizontalScrollBar().isVisible()) \
            .build()

    def _init_scrollable(self,
                         vert_scrollbar_widget: 'ScrollBarWidgetMixin',
                         hor_scrollbar_widget: 'ScrollBarWidgetMixin'):
        self.add_child(vert_scrollbar_widget)
        self.add_child(hor_scrollbar_widget)


class TableWidget(ScrollableWidgetObject):
    def __init__(self, widget_name: str, widget: QtW.QWidget = None,
                 attrs: AttrHolder = None,
                 vals: WidgetValsHolder = None):
        super().__init__(widget_name, widget, attrs, vals)
        if widget is None:
            self._default_widget_init()
        if attrs is None:
            self._default_attrs_init()

    def _default_widget_init(self):
        tb = QWidgetFactory.create_qtable()
        self._widget = tb
        self._init_scrollable(
            VertScrollBarWidget(WidgetNames.get_description_name(
                VertScrollBarWidget.__name__),
                self.widget.verticalScrollBar()),
            HorScrollBarWidget(WidgetNames.get_description_name(
                HorScrollBarWidget.__name__),
                self.widget.horizontalScrollBar()))

    def get_relative_geometry(self,
                              format_: GeometryOutputDataFormat) -> \
            'WidgetGeometry':
        return super().get_relative_geometry(format_)

    def add_child(self, child_widget: WidgetObjectMixin) -> NoReturn:
        super().add_child(child_widget)


class TextAreaWidget(ScrollableWidgetObject):
    def __init__(self, widget_name: str, widget: QtW.QWidget = None,
                 attrs: AttrHolder = None,
                 vals: WidgetValsHolder = None):
        super().__init__(widget_name, widget, attrs, vals)
        if widget is None:
            self._default_widget_init()
        if attrs is None:
            self._default_attrs_init()

    def _default_widget_init(self):
        edit = QWidgetFactory.create_qtextedit()
        self._widget = edit
        self._init_scrollable(
            VertScrollBarWidget(WidgetNames.get_description_name(
                VertScrollBarWidget.__name__),
                self.widget.verticalScrollBar()),
            HorScrollBarWidget(WidgetNames.get_description_name(
                HorScrollBarWidget.__name__),
                self.widget.horizontalScrollBar()))

    def get_relative_geometry(self,
                              format_: GeometryOutputDataFormat) -> \
            'WidgetGeometry':
        return super().get_relative_geometry(format_)

    def add_child(self, child_widget: WidgetObjectMixin) -> NoReturn:
        super().add_child(child_widget)


class TreeViewWidget(ScrollableWidgetObject):
    def __init__(self, widget_name: str, widget: QtW.QWidget = None,
                 attrs: AttrHolder = None,
                 vals: WidgetValsHolder = None):
        super().__init__(widget_name, widget, attrs, vals)
        if widget is None:
            self._default_widget_init()
        if attrs is None:
            self._default_attrs_init()

    def _default_widget_init(self):
        tree_widget = QWidgetFactory.create_qtreewidget()
        self._widget = tree_widget
        self._init_scrollable(
            VertScrollBarWidget(WidgetNames.get_description_name(
                VertScrollBarWidget.__name__),
                self.widget.verticalScrollBar()),
            HorScrollBarWidget(WidgetNames.get_description_name(
                HorScrollBarWidget.__name__),
                self.widget.horizontalScrollBar()))

    def get_relative_geometry(self,
                              format_: GeometryOutputDataFormat) -> \
            'WidgetGeometry':
        return super().get_relative_geometry(format_)

    def add_child(self, child_widget: WidgetObjectMixin) -> NoReturn:
        super().add_child(child_widget)


class ListWidget(ScrollableWidgetObject):
    def __init__(self, widget_name: str, widget: QtW.QWidget = None,
                 attrs: AttrHolder = None,
                 vals: WidgetValsHolder = None):
        super().__init__(widget_name, widget, attrs, vals)
        if widget is None:
            self._default_widget_init()
        if attrs is None:
            self._default_attrs_init()

    def _default_widget_init(self):
        listWidget = QWidgetFactory.create_qlist()
        self._widget = listWidget
        self._init_scrollable(
            VertScrollBarWidget(WidgetNames.get_description_name(
                VertScrollBarWidget.__name__),
                self.widget.verticalScrollBar()),
            HorScrollBarWidget(WidgetNames.get_description_name(
                HorScrollBarWidget.__name__),
                self.widget.horizontalScrollBar()))

    def get_relative_geometry(self,
                              format_: GeometryOutputDataFormat) -> \
            'WidgetGeometry':
        return super().get_relative_geometry(format_)

    def add_child(self, child_widget: WidgetObjectMixin) -> NoReturn:
        super().add_child(child_widget)


class RadioButtonWidget(WidgetObjectMixin):
    def __init__(self, widget_name: str, widget: QtW.QWidget = None,
                 attrs: AttrHolder = None,
                 vals: WidgetValsHolder = None):
        super().__init__(widget_name, widget, attrs, vals)
        if widget is None:
            self._default_widget_init()
        if attrs is None:
            self.__default_attrs_init()

    def _default_widget_init(self):
        rb = QWidgetFactory.create_qradiobutton()
        self._widget = rb

    def __default_attrs_init(self):
        rb = self._widget
        self._attrs = AttrHolderBuilder().checkable(rb.isChecked()).enableable(
            rb.isEnabled()).build()


class CheckBoxWidget(WidgetObjectMixin):
    def __init__(self, widget_name: str, widget: QtW.QCheckBox = None,
                 attrs: AttrHolder = None,
                 vals: WidgetValsHolder = None):
        super().__init__(widget_name, widget, attrs, vals)
        if widget is None:
            self._default_widget_init()
        if attrs is None:
            self.__attr_init()

    def _default_widget_init(self):
        cb = QWidgetFactory.create_qcheckbox()
        self._widget = cb

    def __attr_init(self):
        cb = self.widget
        self._attrs = AttrHolderBuilder().checkable(cb.isChecked()).enableable(
            cb.isEnabled()).build()

    def get_relative_geometry(self,
                              format_: GeometryOutputDataFormat) \
            -> 'WidgetGeometry':
        return super(CheckBoxWidget, self).get_relative_geometry(format_)


class LabelWidget(WidgetObjectMixin):
    def __init__(self, widget_name: str, widget: QtW.QLabel = None,
                 attrs: AttrHolder = None,
                 vals: WidgetValsHolder = None,
                 words_count_range: Tuple[int, int] = None):
        super().__init__(widget_name, widget, attrs, vals)
        self.words_range = words_count_range
        if widget is None:
            self._default_widget_init()
        if attrs is None:
            self.__default_attrs_init()

    def add_child(self, child_widget: WidgetObjectMixin) -> NoReturn:
        super().add_child(child_widget)

    def _default_widget_init(self):
        label = \
            QWidgetFactory.create_qlabel(words_count_range=self.words_range)
        self._widget = label

    def __default_attrs_init(self):
        label = self._widget
        self._attrs = AttrHolderBuilder() \
            .enableable(label.isEnabled()) \
            .text(label.text()) \
            .build()


class ScrollBarWidgetMixin(ContainerWidgetObjectMixin, ABC):
    def __init__(self, widget_name: str, widget: QtW.QWidget = None,
                 attrs: AttrHolder = None,
                 vals: WidgetValsHolder = None):
        super().__init__(widget_name, widget, attrs, vals)

        if widget is None:
            self._default_widget_init()
        if attrs is None:
            self._default_attrs_init()

    def _default_widget_init(self):
        sb = QScrollBar()
        self._widget = sb

    def _default_attrs_init(self):
        sb = self._widget
        self._attrs = AttrHolderBuilder().enableable(sb.isEnabled()).build()

    def get_relative_geometry(self,
                              format_: GeometryOutputDataFormat) -> \
            'WidgetGeometry':
        if self._widget.isVisible():
            return super().get_relative_geometry(format_)
        else:
            return super(WidgetObjectMixin, self).get_relative_geometry(
                format_)


class VertScrollBarWidget(ScrollBarWidgetMixin):
    def __init__(self, widget_name: str, widget: QtW.QWidget = None,
                 attrs: AttrHolder = None,
                 vals: WidgetValsHolder = None):
        super().__init__(widget_name, widget, attrs, vals)
        self._up_btn = ScrollBarButtonWidget(
            WidgetNames.get_description_name(ScrollBarButtonWidget.__name__),
            self.widget,
            ScrollbarButtonType.UP)
        self._down_btn = ScrollBarButtonWidget(
            WidgetNames.get_description_name(ScrollBarButtonWidget.__name__),
            self.widget,
            ScrollbarButtonType.DOWN)
        self.add_child(self._up_btn)
        self.add_child(self._down_btn)

    def add_child(self, child_widget: WidgetObjectMixin) -> NoReturn:
        super().add_child(child_widget)

    @property
    def up_button(self):
        return self._up_btn

    @property
    def down_button(self):
        return self._down_btn


class HorScrollBarWidget(ScrollBarWidgetMixin):
    def __init__(self, widget_name: str, widget: QtW.QWidget = None,
                 attrs: AttrHolder = None,
                 vals: WidgetValsHolder = None):
        super().__init__(widget_name, widget, attrs, vals)
        self._left_button = ScrollBarButtonWidget(
            WidgetNames.get_description_name(ScrollBarButtonWidget.__name__),
            self.widget,
            ScrollbarButtonType.LEFT)
        self._right_btn = ScrollBarButtonWidget(
            WidgetNames.get_description_name(ScrollBarButtonWidget.__name__),
            self.widget,
            ScrollbarButtonType.RIGHT)
        self.add_child(self._left_button)
        self.add_child(self._right_btn)

    def add_child(self, child_widget: WidgetObjectMixin) -> NoReturn:
        super().add_child(child_widget)

    @property
    def left_button(self):
        return self._left_button

    @property
    def right_button(self):
        return self._right_btn


class ScrollBarButtonWidget(ButtonWidget):
    def __init__(self, widget_name: str, parent: QtW.QScrollBar,
                 button_type: ScrollbarButtonType,
                 attrs: AttrHolder = None, vals: WidgetValsHolder = None):
        super().__init__(widget_name, None, attrs, vals)
        self._type = button_type
        self._parent = parent
        if attrs is None:
            self._default_attrs_init()
        if vals is None:
            self._default_vals_init()

    @property
    def widget(self) -> QtW.QWidget:
        raise RuntimeError("In Qt scrollbar's button is hidden under "
                           "abstraction. Cant call it")

    def _default_attrs_init(self):
        self._attrs = AttrHolderBuilder().enableable(True).has_text(False) \
            .iconed(True).build()

    def _default_vals_init(self):
        self._values = WidgetValsHolderBuilder().text('""').build()

    def get_relative_geometry(self, format_: GeometryOutputDataFormat) \
            -> 'WidgetGeometry':
        widget_enum = WidgetNames.get_enum_by_woclassname(
            self.__class__.__name__)
        if self._parent.isVisible():
            return WidgetGeometryAbsFactory.get_widget_geometry_factory(
                format_).create_scrollbar_button_geometry(
                widget_enum.padding,
                self._type,
                self._parent)
        else:
            return super(WidgetObjectMixin, self).get_relative_geometry(
                format_)
