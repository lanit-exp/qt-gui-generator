from enum import Enum

from PySide6 import QtWidgets as QtW


class GeometryOutputDataFormat(Enum):
    YOLO = "YOLO"
    COCO = "COCO"


class AttributesDataFormat(Enum):
    CSV = "CSV"

class ValuesDataFormat(Enum):
    CSV = "CSV"


class MainWindowAccessObject:
    __root_widget = None

    @classmethod
    def set_main_window(cls, root_widget: QtW.QMainWindow):
        cls.__root_widget = root_widget

    @classmethod
    def get_main_window(cls) -> QtW.QMainWindow:
        if cls.__root_widget is None:
            raise RuntimeError("QMainWindow is not initialized")
        return cls.__root_widget