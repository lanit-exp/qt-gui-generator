#!/usr/bin/python

"""
ZetCode PySide tutorial

This program centers a window
on the screen.

author: Jan Bodnar
website: zetcode.com
"""

import sys

from PySide6 import QtWidgets as QtW


class Example(QtW.QWidget):
    def __init__(self):
        super(Example, self).__init__()

        self.initUI()

    def initUI(self):
        self.resize(400, 400)

        self.setWindowTitle('Center')
        self.show()


def main():
    app = QtW.QApplication(sys.argv)
    ex = Example()
    gl = QtW.QFormLayout()
    hl = QtW.QHBoxLayout()
    ex.setLayout(hl)

    glw = QtW.QWidget()
    glw.setLayout(gl)
    hl.addWidget(glw)
    hl.addWidget(QtW.QScrollBar())

    ll = QtW.QLabel()
    ll.setText("TITLEDFS GKSffffffffffffffffffffffffffffffffl")
    gl.addWidget(ll)
    for i in range(3):
        label = QtW.QLabel()
        label.setText("test" + str(i))
        gl.addWidget(QtW.QLabel())
        le = QtW.QLineEdit()

        gl.addRow(label, le)



    gl.SetMinAndMaxSize

    sys.exit(app.exec_())


def main1():
    app = QtW.QApplication(sys.argv)
    cent_wid_layout = QtW.QHBoxLayout()
    window = QtW.QMainWindow()

    #te = QWidgetGeneration.generate_qtextedit()
    #cent_wid_layout.addWidget(te)
    cent_widget = QtW.QWidget()
    cent_widget.setLayout(cent_wid_layout)
    window.setCentralWidget(cent_widget)

    menu_bar = QtW.QMenuBar()
    menu_bar.addMenu("olo1")
    menu_bar.addMenu("olo2")
    window.setMenuBar(menu_bar)

    list_ = menu_bar.actions()
    for item in list_:
        print(menu_bar.actionGeometry(item))

    window.show()
    sys.exit(app.exec_())


def solo_label_from_layout_test():
    app = QtW.QApplication(sys.argv)
    cent_wid_layout = QtW.QFormLayout()
    window = QtW.QMainWindow()

    label = QtW.QLabel('TEST')
    label1 = QtW.QLabel('test')
    edit = QtW.QLineEdit()
    edit1 = QtW.QLineEdit()

    cent_wid_layout.addRow(label)
    cent_wid_layout.addRow(edit)
    cent_wid_layout.addRow(label1, edit1)
    cent_widget = QtW.QWidget()
    cent_widget.setLayout(cent_wid_layout)
    window.setCentralWidget(cent_widget)

    menu_bar = QtW.QMenuBar()
    menu_bar.addMenu("olo1")
    menu_bar.addMenu("olo2")
    window.setMenuBar(menu_bar)

    list_ = menu_bar.actions()
    for item in list_:
        print(menu_bar.actionGeometry(item))

    window.show()
    sys.exit(app.exec_())

class MyObj:
        name = 'Chuck Norris'
        phone = '+666111000'

def main4():
    setattr(MyObj, 'phone', '+600000000')
    setattr(MyObj, 'country', 'Norway')

    # Получим атрибуты из объекта MyObj:
    human = MyObj()
    x = getattr(human, 'phone', '+600000000')
    y = human.country
    print(x, y)

if __name__ == '__main__':
    # main4()

    app = QtW.QApplication(sys.argv)
    cent_wid_layout = QtW.QFormLayout()
    window = QtW.QMainWindow()

    label = QtW.QLabel('TEST')
    label1 = QtW.QLabel('test')
    edit = QtW.QLineEdit()
    edit1 = QtW.QLineEdit()

    cent_wid_layout.addRow(label)
    cent_wid_layout.addRow(edit)
    cent_wid_layout.addRow(label1, edit1)
    cent_widget = QtW.QWidget()
    cent_widget.setLayout(cent_wid_layout)
    window.setCentralWidget(cent_widget)

    menu_bar = QtW.QMenuBar()
    menu_bar.addMenu("olo1")
    menu_bar.addMenu("olo2")
    window.setMenuBar(menu_bar)

    list_ = menu_bar.actions()
    for item in list_:
        print(menu_bar.actionGeometry(item))

    print(a)

    window.show()
    sys.exit(app.exec_())

