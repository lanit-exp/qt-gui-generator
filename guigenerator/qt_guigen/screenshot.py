from datetime import datetime
from pathlib import Path
from random import choice
from typing import Dict, Callable, Tuple

import PySide6.QtGui as QtG
import PySide6.QtWidgets as QtW
from PIL import Image
from PySide6.QtCore import QTimer

import \
    guigenerator.qt_guigen.widgets.widgetobject.wo_concrete as wo
from guigenerator.qt_guigen.config import PyQtGuiGenConfig
from guigenerator.qt_guigen.widgets.widget_geometry import WidgetGeometry, \
    WidgetGeometryUtils
from guigenerator.qt_guigen.widgets.widget_names import WidgetNames
from guigenerator.qt_guigen.widgets.widgetobject.wo_abc import \
    ContainerWidgetObjectMixin
from guigenerator.utils import Utils


class ScreenshotHandler:
    __config = PyQtGuiGenConfig.get_section("DatasetGeneration")

    SCREENSHOT_FORMAT = __config.get("screenshot_format")
    SCREENSHOT_QUALITIES = __config.get_list("screenshot_qualities")
    APP_SCREENSHOTS_PATH = __config.get_path("app_screenshots_dir_path")
    WIDGET_SCREENSHOTS_PATH = __config.get_path("widget_screenshots_dir_path")
    MILLIS_BEFORE_TAB_PRESSED = __config.get_int("millis_before_tab_pressed")
    MILLIS_BEFORE_SCREENSHOT = __config.get_int("millis_before_screenshot")
    MILLIS_BEFORE_APP_EXIT = __config.get_int("millis_before_app_exit")

    SCREENSHOT_MARGIN = PyQtGuiGenConfig.get_section("WidgetGeometry").get_int(
        "default_screenshot_margin")
    WIDGETS_FOR_EXPORT = PyQtGuiGenConfig.get_section(
        "AttributeDataExport").get_list("widgets_for_export")

    FOCUS_WIDGET_NAMES = __config.get_list("focus_widgets")

    APP_SCREENSHOTS_PATH.mkdir(parents=True, exist_ok=True)
    WIDGET_SCREENSHOTS_PATH.mkdir(parents=True, exist_ok=True)

    @classmethod
    def take_main_screenshot(cls, main_window: wo.MainWindowWidget,
                             do_while_taking: Callable) -> 'Screenshot':
        take_mw_screenshot_function, screenshot \
            = cls.__get_take_main_window_screenshot_function(
            main_window.widget)
        QTimer.singleShot(cls.MILLIS_BEFORE_TAB_PRESSED,
                          cls.__get_func_to_focus_widget(main_window))
        QTimer.singleShot(cls.MILLIS_BEFORE_SCREENSHOT,
                          take_mw_screenshot_function)
        QTimer.singleShot(cls.MILLIS_BEFORE_SCREENSHOT, do_while_taking)
        QTimer.singleShot(cls.MILLIS_BEFORE_APP_EXIT, QtG.QGuiApplication.quit)

        QtG.QGuiApplication.exec_()

        return screenshot

    @classmethod
    def __get_func_to_focus_widget(
            cls,
            main_window_widget: wo.MainWindowWidget):

        def press_tab_on_rand_widget():
            Utils.press_tab_key()

        def press_tab_on_given_widget():
            Utils.press_tab_key(widget=chosen_widget.widget)

        if cls.FOCUS_WIDGET_NAMES[0] == "random":
            return press_tab_on_rand_widget
        else:
            chosen_widget = cls.__get_rand_widget_for_focusing_of_given_type(
                main_window_widget)
            return press_tab_on_given_widget

    @classmethod
    def __get_rand_widget_for_focusing_of_given_type(cls, root_widget):
        children = []
        for widget_name in cls.FOCUS_WIDGET_NAMES:
            class_name = WidgetNames(widget_name).woclassname
            wo_class = getattr(wo, class_name)
            children.extend(root_widget.find_descendants(wo_class))
        if children:
            chosen_widget = choice(children)
        else:
            chosen_widget = root_widget
        return chosen_widget

    @classmethod
    def __get_take_main_window_screenshot_function(cls,
                                                   main_window:
                                                   QtW.QMainWindow):

        screenshot: QtG.QPixmap = QtG.QPixmap()
        if len(cls.SCREENSHOT_QUALITIES) > 1:
            filenames = [
                f'img-{datetime.now().strftime("%Y%m%d-%H%M%S-%f")}-q' \
                f'{quality}.{cls.SCREENSHOT_FORMAT}'
                for quality in cls.SCREENSHOT_QUALITIES]
        else:
            filenames = [
                f'img-{datetime.now().strftime("%Y%m%d-%H%M%S-%f")}.'
                f'{cls.SCREENSHOT_FORMAT}']

        def _take_screenshot_function():
            x = main_window.geometry().x() - cls.SCREENSHOT_MARGIN
            y = main_window.geometry().y() - cls.SCREENSHOT_MARGIN
            w = main_window.geometry().width() + 2 * cls.SCREENSHOT_MARGIN
            h = main_window.geometry().height() + 2 * \
                cls.SCREENSHOT_MARGIN

            win_id = 0
            screenshot = QtG.QGuiApplication.primaryScreen().grabWindow(win_id,
                                                                        x, y,
                                                                        w, h)

            for i, filename in enumerate(filenames):
                save_path = str(
                    Path(cls.APP_SCREENSHOTS_PATH) / Path(filename))
                q = int(cls.SCREENSHOT_QUALITIES[i])
                screenshot.save(save_path, quality=q)

        best_screenshot_filename = max(enumerate(filenames),
                                       key=lambda x: cls.SCREENSHOT_QUALITIES[
                                           x[0]])[1]
        best_screenshot_save_path = Path(
            cls.APP_SCREENSHOTS_PATH) / best_screenshot_filename
        return _take_screenshot_function, Screenshot(best_screenshot_save_path)

    @classmethod
    def extract_widget_screenshots(cls, screenshot: 'Screenshot',
                                   main_window: ContainerWidgetObjectMixin,
                                   widgets_geom_dict: Dict[
                                       str, Dict[int, WidgetGeometry]]):

        main_window_w = main_window.widget.geometry().width() + 2 * \
                        cls.SCREENSHOT_MARGIN
        main_window_h = main_window.widget.geometry().height() + 2 * \
                        cls.SCREENSHOT_MARGIN

        img: Image = Image.open(screenshot.fullpath)
        for widget_name, geom_dict in widgets_geom_dict:
            if widget_name in cls.WIDGETS_FOR_EXPORT:
                for widget_id, widget_geom in geom_dict.items():
                    geom = WidgetGeometryUtils.convert_yolo_to_coco(
                        widget_geom, main_window_w, main_window_h)
                    left, upper = int(geom.x), int(geom.y)
                    right, lower = left + int(geom.width), upper + int(
                        geom.height)
                    widget_img = img.copy().crop((left, upper, right, lower))

                    filename = Path(
                        widget_name + '-' + screenshot.filestem.split('-q')[
                            0] + '-' + str(widget_id)
                        + screenshot.filesuffix)
                    widget_img.save(
                        Path(cls.WIDGET_SCREENSHOTS_PATH) / filename)


class Screenshot:
    def __init__(self, fullpath: Path):
        self._fullpath = fullpath
        self._size: Tuple[int, int] = -1, -1

    def _set_size(self):
        with Image.open(str(self.fullpath)) as img:
            self._size = img.size

    @property
    def width(self):
        if self._size == (-1, -1):
            self._set_size()

        return self._size[0]

    @property
    def height(self):
        if self._size == (-1, -1):
            self._set_size()

        return self._size[1]

    @property
    def fullpath(self) -> Path:
        return self._fullpath

    @property
    def filename(self):
        return self._fullpath.name

    @property
    def filesuffix(self):
        return self._fullpath.suffix

    @property
    def filestem(self):
        return self._fullpath.stem
