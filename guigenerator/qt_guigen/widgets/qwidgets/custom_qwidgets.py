from abc import ABC, abstractmethod
from typing import Optional

import PySide6.QtGui as QtG
import PySide6.QtWidgets as QtW


class QMyScrollBar(QtW.QScrollBar):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._has_geometry = False

    def showEvent(self, event):
        self.showEvent(event)
        self._has_geometry = True

    @property
    def has_geometry(self):
        return self._has_geometry


class Checkable(ABC):
    @abstractmethod
    def checkbox(self) -> QtW.QCheckBox: pass


class QCheckableLineEdit(QtW.QLineEdit):
    def __init__(self, text: str = "", parent: Optional[QtW.QWidget] = None):
        super().__init__(text, parent)
        self._checkbox = QtW.QCheckBox(self)
        self._checkbox.setCursor(QtG.Qt.ArrowCursor)
        self._checkbox.move(4, 4)
        self._checkbox.setStyleSheet(f'QCheckBox {{background: transparent;}}')
        self._checkbox.lower()
        self.setStyleSheet(
            f'QLineEdit {{padding-left: '
            f'{self._checkbox.sizeHint().width() + 10}px;}}')
        self.setSizePolicy(QtW.QSizePolicy.Minimum, QtW.QSizePolicy.Fixed)
        self.raise_()

    @property
    def checkbox(self) -> QtW.QCheckBox:
        return self._checkbox

    def setEnabled(self, is_enabled: bool):
        self._checkbox.setEnabled(is_enabled)
        super().setEnabled(is_enabled)


class QCheckableComboBox(QtW.QComboBox):
    def __init__(self, parent: Optional[QtW.QWidget] = None):
        super().__init__(parent)
        self._checkbox = QtW.QCheckBox(self)
        self._checkbox.move(4, 4)
        self._checkbox.setCursor(QtG.Qt.ArrowCursor)
        self._checkbox.setStyleSheet(f'QCheckBox {{background: transparent;}}')
        self._checkbox.lower()
        self.setStyleSheet(
            f'QComboBox {{padding-left: '
            f'{self._checkbox.sizeHint().width() + 10}px;}}')
        self.setSizePolicy(QtW.QSizePolicy.Minimum, QtW.QSizePolicy.Fixed)
        self.raise_()

    @property
    def checkbox(self) -> QtW.QCheckBox:
        return self._checkbox

    def setEnabled(self, is_enabled: bool):
        self._checkbox.setEnabled(is_enabled)
        super().setEnabled(is_enabled)
