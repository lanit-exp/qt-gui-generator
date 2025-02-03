from abc import ABC, abstractmethod
from typing import Tuple

import PySide6.QtCore as QtC
import PySide6.QtGui as QtG
import PySide6.QtWidgets as QtW

from guigenerator.qt_guigen.config import PyQtGuiGenConfig
from guigenerator.qt_guigen.widgets import GeometryOutputDataFormat, \
    MainWindowAccessObject
from guigenerator.qt_guigen.widgets.widgetobject.wo_enums import \
    ScrollbarButtonType


class WidgetGeometry:
    def __init__(self, x: float, y: float, width: float, height: float):
        self._x: float = x
        self._y: float = y
        self._width: float = width
        self._height: float = height

    @property
    def x(self) -> float:
        return self._x

    @property
    def y(self) -> float:
        return self._y

    @property
    def height(self) -> float:
        return self._height

    @property
    def width(self) -> float:
        return self._width

    def not_null(self) -> bool:
        return self.width > 0 and self.width > 0

    def __str__(self):
        return f'{self.x} {self.y} {self.width} {self.height}'


class WidgetGeometryAbsFactory:
    @classmethod
    def get_widget_geometry_factory(cls,
                                    format_: GeometryOutputDataFormat) -> \
            'WidgetGeometryFactory':
        if format_ == GeometryOutputDataFormat.YOLO:
            return WidgetYoloGeometryFactory()
        elif format_ == GeometryOutputDataFormat.COCO:
            return WidgetCocoGeometryFactory()
        else:
            raise RuntimeError(f"Wrong data format: {format_}")


class WidgetGeometryFactory(ABC):
    @classmethod
    @abstractmethod
    def create_null_widget_geometry(cls) -> 'WidgetGeometry':
        return WidgetGeometry(0, 0, -1, -1)

    @classmethod
    @abstractmethod
    def create_merged_widget_geometry(cls, widget1: QtW.QWidget,
                                      widget2: QtW.QWidget, padding: int) \
            -> 'WidgetGeometry':
        raise NotImplemented("Trying to invoke abstract method")

    @classmethod
    @abstractmethod
    def create_widget_geometry(cls, widget: QtW.QWidget, padding: int,
                               exclude_scrollbars: bool = False) \
            -> 'WidgetGeometry':
        raise NotImplemented("Trying to invoke abstract method")

    @classmethod
    @abstractmethod
    def create_text_geometry(cls, parent_widget: QtW.QWidget,
                             x_offset: int, y_offset: int,
                             text_rect: QtC.QRect, padding: int) \
            -> 'WidgetGeometry':
        raise NotImplemented("Trying to invoke abstract method")

    @classmethod
    @abstractmethod
    def create_menu_widget_geometry(cls, id_: int, padding: int,
                                    menu_widget: QtW.QMenu):
        raise NotImplemented("Trying to invoke abstract method")

    @classmethod
    @abstractmethod
    def create_tab_button_geometry(self, padding: int, tab_rect: QtC.QRect):
        raise NotImplemented("Trying to invoke abstract method")

    @classmethod
    @abstractmethod
    def create_scrollbar_button_geometry(cls,
                                         padding: int,
                                         btn_type: ScrollbarButtonType,
                                         parent: QtW.QScrollBar):
        raise NotImplemented("Trying to invoke abstract method")

    @classmethod
    def _merge_widget_geometries(cls, widget1: QtW.QWidget,
                                 widget2: QtW.QWidget):
        geom1 = WidgetGeometryUtils.get_relative_widget_frame_geometry(widget1)
        geom2 = WidgetGeometryUtils.get_relative_widget_frame_geometry(widget2)

        top_left_point1 = widget1.mapTo(widget1.window(), geom1.topLeft())
        top_left_point2 = widget2.mapTo(widget2.window(), geom2.topLeft())

        # init top left point and bottom right point of widget1
        # --------------------------------------------------------
        top_left_point1_x, top_left_point1_y = top_left_point1.x(), \
                                               top_left_point1.y()
        bot_right_point1_x, bot_right_point1_y = top_left_point1_x + \
                                                 geom1.width(), \
                                                 top_left_point1_y + \
                                                 geom1.height()

        # init top left point and bottom right point of widget2
        # --------------------------------------------------------
        top_left_point2_x, top_left_point2_y = top_left_point2.x(), \
                                               top_left_point2.y()
        bot_right_point2_x, bot_right_point2_y = top_left_point2_x + \
                                                 geom2.width(), \
                                                 top_left_point2_y + \
                                                 geom2.height()

        # calculate union of two widgets geometries
        # ---------------------------------------------------------------------
        top_left_point_res = (min(top_left_point1_x, top_left_point2_x),
                              min(top_left_point1_y, top_left_point2_y))
        bot_right_point_res = (max(bot_right_point1_x, bot_right_point2_x),
                               max(bot_right_point1_y, bot_right_point2_y))

        return top_left_point_res, bot_right_point_res

    @classmethod
    def _calculate_merged_geometry_with_center_point(cls, widget1: QtW.QWidget,
                                                     widget2: QtW.QWidget) \
            -> Tuple[int, int, int, int]:
        tl_x, tl_y, w, h \
            = cls._calculate_merged_geometry_with_top_left_point(widget1,
                                                                 widget2)
        center_x = int(tl_x + w / 2.0)
        center_y = int(tl_y + h / 2.0)
        return center_x, center_y, w, h

    @classmethod
    def _calculate_merged_geometry_with_top_left_point(cls, widget1, widget2) \
            -> Tuple[int, int, int, int]:
        top_left_point, bot_right_point = cls._merge_widget_geometries(widget1,
                                                                       widget2)
        tl_x, tl_y = top_left_point
        br_x, br_y = bot_right_point
        w = abs(br_x - tl_x)
        h = abs(br_y - tl_y)
        return tl_x, tl_y, w, h

    @classmethod
    def _create_normalized_geometry(cls, center_x: int, center_y: int, w: int,
                                    h: int,
                                    padding: int,
                                    widget: QtW.QWidget) -> WidgetGeometry:
        w, h = WidgetGeometryUtils.apply_bbox_padding(w, h, padding)
        x, y = WidgetGeometryUtils.apply_screenshot_margin(
            center_x, center_y, widget)
        screen_width, screen_height = \
            WidgetGeometryUtils.calculate_screen_size()
        return WidgetGeometry(x / screen_width, y / screen_height,
                              w / screen_width, h / screen_height)

    @classmethod
    def _create_standard_geometry(cls, top_left_x: int, top_left_y: int,
                                  w: int, h: int,
                                  padding: int,
                                  widget: QtW.QWidget) -> WidgetGeometry:
        w, h = WidgetGeometryUtils.apply_bbox_padding(w, h, padding)
        x, y = WidgetGeometryUtils.apply_screenshot_margin(
            top_left_x, top_left_y, widget)
        x, y = WidgetGeometryUtils \
            .apply_bbox_padding_for_top_left_point(x, y, padding)
        return WidgetGeometry(x, y, w, h)

    @classmethod
    def _get_scrollbar_btn_rect(cls, btn_type: ScrollbarButtonType,
                                parent_x: int,
                                parent_y: int,
                                parent_w: int,
                                parent_h: int):
        magic_number = 15

        if btn_type == ScrollbarButtonType.UP:
            x = parent_x
            y = parent_y
            w = parent_w
            h = magic_number
        elif btn_type == ScrollbarButtonType.RIGHT:
            x = parent_x + parent_w - magic_number
            y = parent_y
            w = magic_number
            h = parent_h
        elif btn_type == ScrollbarButtonType.DOWN:
            x = parent_x
            y = parent_y + parent_h - magic_number
            w = parent_w
            h = magic_number
        elif btn_type == ScrollbarButtonType.LEFT:
            x = parent_x
            y = parent_y
            w = magic_number
            h = parent_h
        else:
            raise RuntimeError("Getting scrollbar button geometry: should "
                               "come here ")
        return x, y, w, h


class WidgetYoloGeometryFactory(WidgetGeometryFactory):
    @classmethod
    def create_null_widget_geometry(cls) -> 'WidgetGeometry':
        return super().create_null_widget_geometry()

    @classmethod
    def create_merged_widget_geometry(cls, widget1: QtW.QWidget,
                                      widget2: QtW.QWidget, padding: int) \
            -> 'WidgetGeometry':
        center_x, center_y, w, h = \
            cls._calculate_merged_geometry_with_center_point(
                widget1, widget2)
        return cls._create_normalized_geometry(center_x, center_y, w, h,
                                               padding, widget1)

    @classmethod
    def create_widget_geometry(cls, widget: QtW.QWidget, padding: int,
                               exclude_scrollbars: bool = False) \
            -> 'WidgetGeometry':
        widget_frame_geometry: QtC.QRect = \
            WidgetGeometryUtils.get_relative_widget_frame_geometry(
                widget)
        if exclude_scrollbars and isinstance(widget, QtW.QAbstractScrollArea):
            WidgetGeometryUtils \
                .exclude_scroll_bars_from_geometry(widget,
                                                   widget_frame_geometry)

        center_point = widget.mapTo(widget.window(),
                                    widget_frame_geometry.center())
        w, h = widget_frame_geometry.width(), widget_frame_geometry.height()
        return cls._create_normalized_geometry(center_point.x(),
                                               center_point.y(), w, h, padding,
                                               widget)

    @classmethod
    def create_menu_widget_geometry(cls, id_: int, padding: int,
                                    menu_widget: QtW.QMenu):
        main_window = MainWindowAccessObject.get_main_window()

        frame_width, frame_height \
            = WidgetGeometryUtils.get_widget_window_frame_width_and_height(
            main_window.centralWidget().window())

        menu_frame_geometry = \
            WidgetGeometryUtils.get_relative_action_frame_geometry(
                main_window.menuWidget(), id_) \
                .adjusted(-frame_width, -frame_height, -frame_width,
                          -frame_height)

        center_point = menu_widget.mapTo(menu_widget.window(),
                                         menu_frame_geometry.center())

        w, h = menu_frame_geometry.width(), menu_frame_geometry.height()
        return cls._create_normalized_geometry(center_point.x(),
                                               center_point.y(), w, h, padding,
                                               main_window.menuWidget())

    @classmethod
    def create_tab_button_geometry(cls, padding: int, tab_rect: QtC.QRect):
        center_widget = MainWindowAccessObject.get_main_window(

        ).centralWidget()
        center_point = center_widget.mapTo(center_widget.window(),
                                           tab_rect.center())

        w, h = tab_rect.width(), tab_rect.height()
        return cls._create_normalized_geometry(center_point.x(),
                                               center_point.y(), w, h, padding,
                                               center_widget)

    @classmethod
    def create_text_geometry(cls, parent_widget: QtW.QWidget,
                             x_offset: int, y_offset: int,
                             text_rect: QtC.QRect, padding: int) \
            -> 'WidgetGeometry':
        top_left_point = parent_widget.mapTo(parent_widget.window(),
                                             text_rect.topLeft())
        w, h = text_rect.width(), text_rect.height()
        return cls._create_normalized_geometry(top_left_point.x(),
                                               top_left_point.y(),
                                               w, h, padding, parent_widget)

    @classmethod
    def create_scrollbar_button_geometry(cls,
                                         padding: int,
                                         btn_type: ScrollbarButtonType,
                                         parent: QtW.QScrollBar):
        center_widget = MainWindowAccessObject.get_main_window() \
            .centralWidget()

        widget_frame_geometry: QtC.QRect = \
            WidgetGeometryUtils.get_relative_widget_frame_geometry(
                parent)

        top_left_point = parent.mapTo(parent.window(),
                                      widget_frame_geometry.topLeft())
        w, h = widget_frame_geometry.width(), widget_frame_geometry.height()
        x, y, w, h = cls._get_scrollbar_btn_rect(btn_type, top_left_point.x(),
                                                 top_left_point.y(), w, h)
        center_x = x + w // 2
        center_y = y + w // 2

        return cls._create_normalized_geometry(center_x, center_y, w, h,
                                               padding, center_widget)


class WidgetCocoGeometryFactory(WidgetGeometryFactory):
    @classmethod
    def create_null_widget_geometry(cls) -> 'WidgetGeometry':
        return super().create_null_widget_geometry()

    @classmethod
    def create_merged_widget_geometry(cls, widget1: QtW.QWidget,
                                      widget2: QtW.QWidget,
                                      padding: int) -> 'WidgetGeometry':
        top_left_x, top_left_y, w, h \
            = cls._calculate_merged_geometry_with_top_left_point(widget1,
                                                                 widget2)
        return cls._create_standard_geometry(top_left_x, top_left_y, w, h,
                                             padding, widget1)

    @classmethod
    def create_widget_geometry(cls, widget: QtW.QWidget, padding: int,
                               exclude_scrollbars: bool = False) -> \
            'WidgetGeometry':
        widget_frame_geometry: QtC.QRect = \
            WidgetGeometryUtils.get_relative_widget_frame_geometry(
                widget)
        if exclude_scrollbars and isinstance(widget, QtW.QAbstractScrollArea):
            WidgetGeometryUtils \
                .exclude_scroll_bars_from_geometry(widget,
                                                   widget_frame_geometry)

        top_left_point = widget.mapTo(widget.window(),
                                      widget_frame_geometry.topLeft())
        w, h = widget_frame_geometry.width(), widget_frame_geometry.height()
        return cls._create_standard_geometry(top_left_point.x(),
                                             top_left_point.y(),
                                             w, h, padding, widget)

    @classmethod
    def create_text_geometry(cls, parent_widget: QtW.QWidget,
                             x_offset: int, y_offset: int,
                             text_rect: QtC.QRect, padding: int) \
            -> 'WidgetGeometry':
        parent_widget_rect = WidgetGeometryUtils \
            .get_relative_widget_frame_geometry(parent_widget)
        top_left_point = parent_widget.mapTo(parent_widget.window(),
                                             parent_widget_rect.topLeft())
        w, h = text_rect.width(), text_rect.height()
        return cls._create_standard_geometry(top_left_point.x() + x_offset,
                                             top_left_point.y() + y_offset,
                                             w, h, padding, parent_widget)

    @classmethod
    def create_menu_widget_geometry(cls, id_: int, padding: int,
                                    menu_widget: QtW.QMenu):
        main_window = MainWindowAccessObject.get_main_window()
        menu_frame_geometry = \
            WidgetGeometryUtils.get_relative_action_frame_geometry(
                main_window.menuWidget(), id_)
        top_left_point = menu_widget.mapTo(menu_widget.window(),
                                           menu_frame_geometry.topLeft())

        w, h = menu_frame_geometry.width(), menu_frame_geometry.height()
        return cls._create_standard_geometry(top_left_point.x(),
                                             top_left_point.y(), w, h, padding,
                                             main_window.menuWidget())

    @classmethod
    def create_tab_button_geometry(cls, padding: int, tab_rect: QtC.QRect):
        center_widget = MainWindowAccessObject.get_main_window(

        ).centralWidget()
        top_left_point = center_widget.mapTo(center_widget.window(),
                                             tab_rect.topLeft())

        w, h = tab_rect.width(), tab_rect.height()
        return cls._create_standard_geometry(top_left_point.x(),
                                             top_left_point.y(),
                                             w, h, padding, center_widget)

    @classmethod
    def create_scrollbar_button_geometry(cls,
                                         padding: int,
                                         btn_type: ScrollbarButtonType,
                                         parent: QtW.QScrollBar):
        center_widget = MainWindowAccessObject.get_main_window() \
            .centralWidget()

        widget_frame_geometry: QtC.QRect = \
            WidgetGeometryUtils.get_relative_widget_frame_geometry(
                parent)

        top_left_point = parent.mapTo(parent.window(),
                                      widget_frame_geometry.topLeft())
        w, h = widget_frame_geometry.width(), widget_frame_geometry.height()
        x, y, w, h = cls._get_scrollbar_btn_rect(btn_type, top_left_point.x(),
                                                 top_left_point.y(), w, h)
        return cls._create_standard_geometry(x, y, w, h,
                                             padding, center_widget)


class WidgetGeometryUtils:
    __config = PyQtGuiGenConfig.get_section("WidgetGeometry")

    WIDGET_BBOX_PADDING = __config.get_int("default_widget_bbox_padding")
    SCREENSHOT_MARGIN = __config.get_int("default_screenshot_margin")

    @classmethod
    def convert_yolo_to_coco(cls, geom: WidgetGeometry, window_w: int,
                             window_h: int) -> WidgetGeometry:
        w, h = geom.width * window_w, geom.height * window_h
        x, y = int(geom.x * window_w - w / 2.0), int(
            geom.y * window_h - h / 2.0)
        return WidgetGeometry(x, y, w, h)

    @classmethod
    def get_relative_widget_frame_geometry(cls,
                                           widget: QtW.QWidget) -> QtC.QRect:
        frame_width, frame_height \
            = cls.get_widget_window_frame_width_and_height(widget.window())
        rect = widget.rect().adjusted(-frame_width, -frame_height,
                                      -frame_width, -frame_height)
        return rect

    @classmethod
    def get_relative_action_frame_geometry(cls, action_holder: QtW.QWidget,
                                           id_: int) -> QtC.QRect:
        action: QtG.QAction = action_holder.actions()[id_]
        ag = action_holder.actionGeometry(action)
        return ag

    @classmethod
    def get_widget_window_frame_width_and_height(cls, widget: QtW.QWidget) -> \
            Tuple[int, int]:
        g = widget.window().geometry()
        fg = widget.window().frameGeometry()
        return (fg.width() - g.width()), (fg.height() - g.height())

    @classmethod
    def calculate_screen_size(cls) -> Tuple[int, int]:
        main_window = MainWindowAccessObject.get_main_window()
        root_frame_geometry: QtC.QRect = \
            WidgetGeometryUtils.get_relative_widget_frame_geometry(
                main_window.window())
        screen_width = root_frame_geometry.width() + 2 * \
                       WidgetGeometryUtils.SCREENSHOT_MARGIN
        screen_height = root_frame_geometry.height() + 2 * \
                        WidgetGeometryUtils.SCREENSHOT_MARGIN
        return screen_width, screen_height

    @classmethod
    def apply_screenshot_margin(cls, center_x: int, center_y: int,
                                widget: QtW.QWidget) \
            -> Tuple[int, int]:
        x_frame_offset, y_frame_offset = \
            cls.get_widget_window_frame_width_and_height(
                widget)
        x = center_x + x_frame_offset + cls.SCREENSHOT_MARGIN
        y = center_y + y_frame_offset + cls.SCREENSHOT_MARGIN
        return x, y

    @classmethod
    def apply_bbox_padding(cls, width: int, height: int, padding: int) -> \
            Tuple[int, int]:
        width += 2 * padding
        height += 2 * padding
        return width, height

    @classmethod
    def apply_bbox_padding_for_top_left_point(cls, x, y, padding):
        return x - padding, y - padding

    @classmethod
    def exclude_scroll_bars_from_geometry(cls, widget: QtW.QWidget,
                                          geometry: QtC.QRect):
        vertical_scroll_bar = widget.verticalScrollBar()
        if vertical_scroll_bar.isVisible():
            shrank_width = geometry.width() - vertical_scroll_bar.width()
            geometry.setWidth(shrank_width)
        horizontal_scroll_bar = widget.horizontalScrollBar()
        if horizontal_scroll_bar.isVisible():
            shrank_height = geometry.height() - horizontal_scroll_bar.height()
            geometry.setHeight(shrank_height)
