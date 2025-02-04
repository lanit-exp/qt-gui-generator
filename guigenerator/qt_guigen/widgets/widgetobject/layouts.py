from guigenerator.dto.tree_dto import TreeDto
from PySide6 import QtWidgets as QtW
from PySide6.QtCore import Qt, QMargins, QPoint, QRect, QSize

from guigenerator.qt_guigen.widgets.widget_names import WidgetNames


class FlowLayout(QtW.QLayout):
    def __init__(self, parent=None):
        super().__init__(parent)

        if parent is not None:
            self.setContentsMargins(QMargins(0, 0, 0, 0))

        self._item_list = []

    def __del__(self):
        item = self.takeAt(0)
        while item:
            item = self.takeAt(0)

    def addItem(self, item):
        self._item_list.append(item)

    def count(self):
        return len(self._item_list)

    def itemAt(self, index):
        if 0 <= index < len(self._item_list):
            return self._item_list[index]

        return None

    def takeAt(self, index):
        if 0 <= index < len(self._item_list):
            return self._item_list.pop(index)

        return None

    def expandingDirections(self):
        return Qt.Orientation(0)

    def hasHeightForWidth(self):
        return True

    def heightForWidth(self, width):
        height = self._do_layout(QRect(0, 0, width, 0), True)
        return height

    def setGeometry(self, rect):
        super(FlowLayout, self).setGeometry(rect)
        self._do_layout(rect, False)

    def sizeHint(self):
        return self.minimumSize()

    def minimumSize(self):
        size = QSize()

        for item in self._item_list:
            size = size.expandedTo(item.minimumSize())

        size += QSize(2 * self.contentsMargins().top(), 2 * self.contentsMargins().top())
        return size

    def _do_layout(self, rect, test_only):
        x = rect.x()
        y = rect.y()
        line_height = 0
        spacing = self.spacing()

        for item in self._item_list:
            style = item.widget().style()
            layout_spacing_x = style.layoutSpacing(
                QtW.QSizePolicy.PushButton,
                QtW.QSizePolicy.PushButton, Qt.Horizontal
            )
            layout_spacing_y = style.layoutSpacing(
                QtW.QSizePolicy.PushButton,
                QtW.QSizePolicy.PushButton, Qt.Vertical
            )
            space_x = spacing + layout_spacing_x
            space_y = spacing + layout_spacing_y
            next_x = x + item.sizeHint().width() + space_x
            if next_x - space_x > rect.right() and line_height > 0:
                x = rect.x()
                y = y + line_height + space_y
                next_x = x + item.sizeHint().width() + space_x
                line_height = 0

            if not test_only:
                item.setGeometry(QRect(QPoint(x, y), item.sizeHint()))

            x = next_x
            line_height = max(line_height, item.sizeHint().height())

        return y + line_height - rect.y()

class FlowLayoutObject(object):
    def __init__(self):
        self._layout = FlowLayout()

    @property
    def layout(self):
        return self._layout

    def add_child(self, widget: QtW.QWidget):
        self._layout.addWidget(widget)



class GridLayoutObject(object):
    def __init__(self, tree_: TreeDto, max_col_before_changing_adding_order: int, max_row: int):
        self._set_init_value_for_upd_from_left_to_right()
        self._max_col_before_changing_adding_order: int = max_col_before_changing_adding_order
        self._max_row = max_row
        self._children_count = self.__count_grid_children(tree_)
        self._children_added = 0
        self._layout = QtW.QGridLayout()

    @property
    def layout(self):
        return self._layout

    @classmethod
    def __count_grid_children(cls, tree: TreeDto) -> int:
        node = tree.root_node
        result = 0
        for child in node.children:
            if WidgetNames(child.name).is_central_widget_child:
                result += 1
        return result


    def add_child(self, widget: QtW.QWidget):
        self._children_added += 1
        if self._children_count == self._children_added:
            self._layout.addWidget(widget, self._row, self._col, -1, -1)
        else:
            self._layout.addWidget(widget, self._row, self._col)
        self._update_row_col()

    def _update_row_col(self):
        widget_before_changing_adding_order = self._max_col_before_changing_adding_order * self._max_row
        if self._children_added <= widget_before_changing_adding_order:
            self._update_from_left_to_right()
        else:
            self._update_from_top_to_bottom()

        if self._children_added == widget_before_changing_adding_order:
            self._set_init_value_for_upd_from_top_to_bottom()

    def _update_from_left_to_right(self):
        self._col += 1
        if self._col >= self._max_col_before_changing_adding_order:
            self._col = 0
            self._row += 1

    def _set_init_value_for_upd_from_left_to_right(self):
        self._row = 0
        self._col = 0

    def _update_from_top_to_bottom(self):
        self._row += 1
        if self._row >= self._max_row:
            self._row = 0
            self._col += 1

    def _set_init_value_for_upd_from_top_to_bottom(self):
        self._row = 0
        self._col = self._max_col_before_changing_adding_order + 1


class LabelGridLayoutObject(GridLayoutObject):
    def add_child(self, widget: QtW.QWidget):
        self._children_added += 1
        if self._children_count == self._children_added:
            self._layout.addWidget(widget, self._row, self._col, -1, -1)
        else:
            self._layout.addWidget(widget, self._row, self._col)
        self._update_row_col()

    def _update_row_col(self):
        widget_before_changing_adding_order = \
            self._max_col_before_changing_adding_order * self._max_row
        if self._children_added <= widget_before_changing_adding_order:
            self._update_from_top_to_bottom()
        else:
            self.__update_from_left_to_right()

        if self._children_added == widget_before_changing_adding_order:
            self._set_init_value_for_upd_from_top_to_bottom()
