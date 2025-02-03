from random import choice, random

from PySide6 import QtGui as QtG

from guigenerator.qt_guigen.config import PyQtGuiGenConfig

FONT_SIZES = PyQtGuiGenConfig.get_section("DatasetGeneration").get_list(
    "font_sizes")
FONT_EXCEPT = PyQtGuiGenConfig.get_section("DatasetGeneration").get_list(
    "fonts_except_list")

def generate_random_font() -> QtG.QFont:
    size = int(choice(FONT_SIZES))
    family = ""
    while (family == "" or family in FONT_EXCEPT):
        family = choice(QtG.QFontDatabase.families())
    style = choice(QtG.QFontDatabase.styles(family))
    font = QtG.QFontDatabase.font(family, style, size)

    print(f"Font -- {font}")
    return font
