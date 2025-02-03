from enum import Enum
from typing import List, Dict

from guigenerator.qt_guigen.config import WidgetObjectDescrConfig, \
    WidgetObjectDescription


class   WidgetNames(Enum):
    __woclassname_to_enum__: Dict[str, 'WidgetNames'] = {}

    WINDOW = ("Window", "MainWindowWidget")

    GROUP_BOX = ("GroupBox", "GroupBoxContainerWidget")
    LINE_EDIT_COMBOBOX_FORM_BOX = ("LineEditComboboxFormBox",
                                   "FormBoxContainerWidget")
    RADIOBUTTON_BOX = ("RadioButtonBox", "FormBoxContainerWidget")
    CHECKBOX_BOX = ("CheckboxBox", "FormBoxContainerWidget")

    LABELED_LINE_EDIT = ("LabeledLineEdit", "LabeledLineEditHFormItemWidget")
    LABELED_CHECKABLE_LINE_EDIT = ("LabeledCheckableLineEdit",
                                   "LabeledCheckableLineEditHFormItemWidget")
    LABELED_COMBOBOX = ("LabeledComboBox", "LabeledComboBoxHFormItemWidget")
    LABELED_CHECKABLE_COMBOBOX = ("LabeledCheckableComboBox",
                                  "LabeledCheckableComboBoxHFormItemWidget")
    LABELED_RADIOBUTTON = ("LabeledRadioButton",
                           "LabeledRadioButtonHFormItemWidget")
    LABELED_CHECKBOX = ("LabeledCheckbox", "LabeledCheckBoxHFormItemWidget")
    LABELED_INPUT = ("LabeledInput", "LabeledInputHFormItemWidget")
    REVERSED_LABELED_LINE_EDIT = ("ReversedLabeledLineEdit",
                                  "RevLabeledLineEditHFormItemWidget")
    REVERSED_LABELED_CHECKABLE_LINE_EDIT \
        = ("ReversedLabeledCheckableLineEdit",
           "RevLabeledCheckableLineEditHFormItemWidget")
    REVERSED_LABELED_COMBOBOX = ("ReversedLabeledComboBox",
                                 "RevLabeledComboBoxHFormItemWidget")
    REVERSED_LABELED_CHECKABLE_COMBOBOX \
        = ("ReversedLabeledCheckableComboBox",
           "RevLabeledCheckableComboBoxHFormItemWidget")
    REVERSED_LABELED_RADIOBUTTON \
        = ("ReversedLabeledRadioButton",
           "RevLabeledRadioButtonHFormItemWidget")
    REVERSED_LABELED_CHECKBOX \
        = ("ReversedLabeledCheckbox",
           "RevLabeledCheckBoxHFormItemWidget")
    REVERSED_LABELED_INPUT \
        = ("ReversedLabeledInput",
           "RevInputEditHFormItemWidget")
    TOP_LABELED_LINE_EDIT \
        = ("TopLabeledLineEdit",
           "TopLabeledLineEditVFormItemWidget")
    TOP_LABELED_CHECKABLE_LINE_EDIT \
        = ("TopLabeledCheckableLineEdit",
           "TopLabeledCheckableLineEditVFormItemWidget")
    TOP_LABELED_CHECKABLE_COMBOBOX \
        = ("TopLabeledCheckableComboBox",
           "TopLabeledCheckableComboBoxVFormItemWidget")
    TOP_LABELED_COMBOBOX \
        = ("TopLabeledComboBox",
           "TopLabeledComboBoxVFormItemWidget")
    TOP_LABELED_RADIOBUTTON \
        = ("TopLabeledRadioButton",
           "TopLabeledRadioButtonVFormItemWidget")
    TOP_LABELED_CHECKBOX \
        = ("TopLabeledCheckbox",
           "TopLabeledCheckBoxVFormItemWidget")
    TOP_LABELED_INPUT = ("TopLabeledInput", "TopLabeledInputVFormItemWidget")

    LIST = ("List", "ListWidget")
    TABLE = ("Table", "TableWidget")
    TEXTAREA = ("TextArea", "TextAreaWidget")
    TREE_VIEW = ("TreeView", "TreeViewWidget")

    MENU_ITEM = ("MenuItem", "MenuItemWidget")
    LABEL = ("Label", "LabelWidget")
    BUTTON = ("Button", "ButtonWidget")
    SCROLL_BAR_BUTTON = ("ScrollBarButton", "ScrollBarButtonWidget")
    CHECKBOX = ("Checkbox", "CheckBoxWidget")
    RADIOBUTTON = ("RadioButton", "RadioButtonWidget")
    LINE_EDIT = ("LineEdit", "LineEditWidget")
    CHECKABLE_LINE_EDIT = ("CheckableLineEdit", "CheckableLineEditWidget")
    COMBOBOX = ("Combobox", "ComboBoxWidget")
    CHECKABLE_COMBOBOX = ("CheckableComboBox", "CheckableComboBoxWidget")
    VERT_SCROLL_BAR = ("VertScrollBar", "VertScrollBarWidget")
    HOR_SCROLL_BAR = ("HorScrollBar", "HorScrollBarWidget")
    STATUS_BAR = ("StatusBar", "StatusBarWidget")
    TAB_BUTTON = ("TabButton", "TabButtonWidget")
    TAB_BAR = ("TabBar", "TabWidget")
    INPUT = ("Input", "InputWidget")
    TEXT_ELEMENT = ("TextElement", "TextElementWidget")

    def __new__(cls, description_name, woclassname):
        obj = object.__new__(cls)
        obj._value_ = description_name
        obj.__woclassname = woclassname
        return obj

    def __init__(self, description_name, woclassname):
        self.__widget_description: WidgetObjectDescription \
            = WidgetObjectDescrConfig.get_widget_object_description(
            description_name)
        self.__link_woclassname_to_enum(self, woclassname)

    @classmethod
    def __link_woclassname_to_enum(cls, enum_obj: 'WidgetNames',
                                   woclassname: str):
        cls.__woclassname_to_enum__[woclassname] = enum_obj

    @classmethod
    def get_enum_by_woclassname(cls, woclassname: str) -> 'WidgetNames':
        if not cls.__woclassname_to_enum__.keys():
            raise RuntimeError("no enum names have been added yet")
        return cls.__woclassname_to_enum__[woclassname]

    @classmethod
    def get_description_name(cls, woclasssname: str) -> str:
        return cls.get_enum_by_woclassname(woclasssname).value

    @classmethod
    def get_possible_enum_names(cls) -> List[str]:
        return list(enum_item.value for enum_item in cls.__members__.values())

    @property
    def min_width(self) -> int:
        return self.__widget_description.min_width

    @property
    def min_height(self) -> int:
        return self.__widget_description.min_height

    @property
    def is_container(self) -> bool:
        return self.__widget_description.container

    @property
    def accept_list(self) -> List[str]:
        return self.__widget_description.accept_list

    @property
    def is_central_widget_child(self) -> bool:
        return self.__widget_description.central_widget_child

    @property
    def woclassname(self) -> str:
        return self.__woclassname

    @property
    def padding(self):
        return self.__widget_description.padding
