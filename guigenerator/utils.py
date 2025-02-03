import glob
from collections import namedtuple
from os.path import dirname, abspath
from pathlib import Path
from typing import Dict, Callable, Any, List

import PySide6.QtCore as QtC
import PySide6.QtGui as QtG

ScreenResolution = namedtuple('ScreenResolution', 'width height')


class Utils:
    SRC_ROOT_DIR: Path = Path(dirname(abspath(__file__)))
    PROJ_ROOT_DIR: Path = Path(SRC_ROOT_DIR).parent
    RESOURCES_DIR: Path = PROJ_ROOT_DIR / "resources"

    @classmethod
    def press_tab_key(cls, widget=None):
        if widget is None:
            widget = QtG.QGuiApplication.topLevelWindows()[0]
        press = QtG.QKeyEvent(QtC.QEvent.KeyPress, QtG.Qt.Key_Tab,
                              QtG.Qt.NoModifier, "a")
        release = QtG.QKeyEvent(QtC.QEvent.KeyRelease, QtG.Qt.Key_Tab,
                                QtG.Qt.NoModifier, "a")
        QtG.QGuiApplication.postEvent(widget, press)
        QtG.QGuiApplication.postEvent(widget, release)

    @classmethod
    def get_icon_paths(cls) -> List[Path]:
        icons = [Path(icon) for icon in glob.glob(
            str(cls.RESOURCES_DIR / 'icons/*.png'))]
        return icons

    @classmethod
    def get_stylesheets_dir_path(cls) -> Path:
        return cls.RESOURCES_DIR / "stylesheets"

    @classmethod
    def get_background_names(cls) -> List[str]:
        bg_paths = map(lambda path_str: Path(path_str),
                       glob.glob(str(cls.RESOURCES_DIR / "bg/*")))
        return [path.name for path in bg_paths]

    @classmethod
    def write_to_json(cls, obj, path: str) -> None:
        def get_object_dict(d):
            return d.__dict__

        from ntpath import split
        from os import makedirs
        from json import dumps

        filepath, _ = split(path)
        if filepath:
            makedirs(filepath, exist_ok=True)
        with open(path, "w") as out:
            json_string = dumps(obj, default=get_object_dict,
                                ensure_ascii=False)
            out.write(json_string)

    @classmethod
    def read_from_json(cls, input_path: str,
                       object_hook_: Callable[[Dict], Any] = None) -> Any:
        from json import load
        with open(input_path, "r", encoding="windows-1251") as fin:
            data = load(fin, object_hook=object_hook_)
        return data

    @classmethod
    def remove_extension(cls, filename: str):
        from os.path import splitext
        filename_without_extension, _ = splitext(filename)
        return filename_without_extension

    __screen_resolution_width: int = -1
    __screen_resolution_height: int = -1

    @classmethod
    def get_screen_resolution(cls) -> ScreenResolution:
        if cls.__screen_resolution_height == -1:
            app = QtG.QGuiApplication
            if app is None:
                raise RuntimeError("QApplication is not instantiated")

            cls.__screen_resolution_width = app.primaryScreen().size().width()
            cls.__screen_resolution_height = app.primaryScreen().size() \
                .height()

        return ScreenResolution(cls.__screen_resolution_width,
                                cls.__screen_resolution_height)

    @classmethod
    def write_to_file(cls, file_path: Path, text: str, mode: str = 'w'):
        dir_path = file_path.parent
        dir_path.mkdir(parents=True, exist_ok=True)
        with open(file_path, mode) as out:
            out.write(text)
