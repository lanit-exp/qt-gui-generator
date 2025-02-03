from random import randint, choice, random
from typing import List, Tuple

from PySide6 import QtWidgets as QtW, QtGui as QtG, QtCore as QtC

from guigenerator.dto.tree_dto import TreeDto
from guigenerator.qt_guigen.config import PyQtGuiGenConfig
from guigenerator.qt_guigen.widgets.qwidgets.custom_qwidgets import \
    QCheckableLineEdit, QCheckableComboBox
from guigenerator.qt_guigen.widgets.random_values_generation.random_font_gen \
    import \
    generate_random_font
from guigenerator.qt_guigen.widgets.random_values_generation \
    .random_numbers_gen import \
    RandNumbersGeneration
from guigenerator.qt_guigen.widgets.random_values_generation.random_text_gen \
    import \
    RandomTextGeneration, TextGenerationStrategy
from guigenerator.utils import Utils

DATASET_GENERATION_CONFIG = PyQtGuiGenConfig.get_section("DatasetGeneration")
CHECKBOX_SIZES = DATASET_GENERATION_CONFIG.get_list("checkbox_sizes")
RADIO_SIZES = DATASET_GENERATION_CONFIG.get_list("radio_sizes")
ROW_EMPHASIZE_COLORS_LIST = DATASET_GENERATION_CONFIG \
    .get_list("table_item_selection_color")
GEN_STRAT = TextGenerationStrategy(DATASET_GENERATION_CONFIG
                                   .get("text_generation_strat"))


class QWidgetFactory:
    _checkbox_count = 0
    _radio_count = 0
    _rand_text_gen = RandomTextGeneration(GEN_STRAT)
    _alignments = [QtC.Qt.AlignLeft, QtC.Qt.AlignCenter, QtC.Qt.AlignRight]

    @classmethod
    def reset_counters(cls):
        cls._checkbox_count = 0
        cls._radio_count = 0

    @classmethod
    def create_qtable(cls) -> QtW.QTableWidget:
        __QTABLE_HHEADER_LABELS_PROB = 0.5
        __QTABLE_ENABLED_PROB = 0.5

        __QTABLE_ROW_COUNT_RANGE = 3, 20
        __QTABLE_COL_COUNT_RANGE = 2, 5

        def _generate_table_item(first_letter: str = "") \
                -> QtW.QTableWidgetItem:
            if first_letter == "":
                label = cls._rand_text_gen.gen_random_str_of_words(1, 1)
            else:
                label = cls._rand_text_gen \
                    .gen_random_str_of_words_starting_with_letter(
                    1, 1, letter).capitalize()
            return QtW.QTableWidgetItem(label)

        def _generate_label_texts(item_amount: int) -> List[str]:
            return [
                cls._rand_text_gen.gen_random_str_of_words(1, 1)
                for _ in range(item_amount)]

        row_count = randint(*__QTABLE_ROW_COUNT_RANGE)
        col_count = randint(*__QTABLE_COL_COUNT_RANGE)
        qtable = QtW.QTableWidget(row_count, col_count)

        is_same_fist_letter = PyQtGuiGenConfig \
            .get_section("DatasetGeneration") \
            .get_boolean("same_first_letter_for_tables_and_lists")
        if is_same_fist_letter:
            letter = choice(cls._rand_text_gen.get_possible_starting_letters())
            for row in range(row_count):
                for col in range(col_count):
                    qtable.setItem(row, col, _generate_table_item(letter))
        else:
            for row in range(row_count):
                for col in range(col_count):
                    qtable.setItem(row, col, _generate_table_item())

        if random() < 0.8 and ROW_EMPHASIZE_COLORS_LIST:
            row_to_emphasize = randint(0, row_count)
            color = choice(ROW_EMPHASIZE_COLORS_LIST)
            qtable.setStyleSheet(
                f"QTableWidget::item{{selection-background-color: {color} }}")
            qtable.selectRow(row_to_emphasize)

        if random() < __QTABLE_HHEADER_LABELS_PROB:
            qtable.setHorizontalHeaderLabels(_generate_label_texts(col_count))
        if random() < 1.0 - __QTABLE_ENABLED_PROB:
            qtable.setEnabled(False)

        qtable.setSizePolicy(QtW.QSizePolicy.MinimumExpanding,
                             QtW.QSizePolicy.MinimumExpanding)
        return qtable

    @classmethod
    def create_qcheckbox(cls) -> QtW.QCheckBox:
        __QCHECKBOX_CHECKED_PROB = 0.5
        __QCHECKBOX_ENABLED_PROB = 0.5
        __QCHECKBOX_FOCUS_PROB = 0.5

        checkbox = QtW.QCheckBox()
        if random() < __QCHECKBOX_CHECKED_PROB:
            checkbox.setChecked(True)
        if random() < 1.0 - __QCHECKBOX_ENABLED_PROB:
            checkbox.setEnabled(False)
        if random() > 1 / len(CHECKBOX_SIZES):
            cls._checkbox_count += 1
            obj_name = f"checkbox{cls._checkbox_count}"
            checkbox.setObjectName(obj_name)
            size = choice(CHECKBOX_SIZES)
            checkbox.setStyleSheet(
                f"""QCheckBox#{obj_name}::indicator {{
                width: {size}px;
                height: {size}px;
                }}
                """
            )
        if random() < __QCHECKBOX_FOCUS_PROB:
            checkbox.setFocus()

        return checkbox

    @classmethod
    def create_qlabel(cls, words_count_range: Tuple[int, int] = None) \
            -> QtW.QLabel:
        if words_count_range is None:
            words_count_start, words_count_end = 1, 1
        else:
            words_count_start, words_count_end = words_count_range

        text = cls._rand_text_gen.gen_random_str_of_words(words_count_start,
                                                          words_count_end)
        label = QtW.QLabel(text)
        label.setWordWrap(True)
        label.setAlignment(QtC.Qt.AlignCenter)
        label.setSizePolicy(QtW.QSizePolicy.Expanding,
                            QtW.QSizePolicy.Expanding)
        label.setContentsMargins(4, 0, 4, 0)
        return label

    @classmethod
    def create_labeled_qcheckbox(cls) -> Tuple[QtW.QLabel, QtW.QCheckBox]:
        label = cls.create_qlabel((3, 4))
        label.setSizePolicy(QtW.QSizePolicy.Expanding,
                            QtW.QSizePolicy.Expanding)
        checkbox = cls.create_qcheckbox()
        return label, checkbox

    @classmethod
    def create_qradiobutton(cls) -> QtW.QRadioButton:
        __QRADIO_CHECKED_PROB = 0.5
        __QRADIO_ENABLED_PROB = 0.5
        __QRADIO_FOCUS_PROB = 0.5

        radio = QtW.QRadioButton()
        if random() < __QRADIO_CHECKED_PROB:
            radio.setChecked(True)
        if random() < 1.0 - __QRADIO_ENABLED_PROB:
            radio.setEnabled(False)
        if random() > 1 / len(RADIO_SIZES):
            cls._radio_count += 1
            obj_name = f"radio{cls._checkbox_count}"
            radio.setObjectName(obj_name)
            size = choice(CHECKBOX_SIZES)
            radio.setStyleSheet(
                f"""QRadioButton#{obj_name}::indicator {{
                width: {size}px;
                height: {size}px;
                }}
                """
            )
        if random() < __QRADIO_FOCUS_PROB:
            radio.setFocus()
        return radio

    @classmethod
    def create_labeled_qradiobutton(cls) -> Tuple[QtW.QLabel,
                                                  QtW.QRadioButton]:
        label = cls.create_qlabel((1, 2))
        label.setSizePolicy(QtW.QSizePolicy.Expanding,
                            QtW.QSizePolicy.Expanding)
        radiobutton = cls.create_qradiobutton()
        return label, radiobutton

    @classmethod
    def create_qwindow(cls, layout: QtW.QLayout,
                       tree_: TreeDto) -> QtW.QMainWindow:
        SCREENSHOT_MARGIN = PyQtGuiGenConfig.get_section(
            "WidgetGeometry").get_int("default_screenshot_margin")

        __QWINDOW_POSITION_COORD: Tuple[int, int] \
            = (SCREENSHOT_MARGIN, SCREENSHOT_MARGIN)
        __QWINDOW_MAX_HEIGHT: int = int(
            Utils.get_screen_resolution().height * 0.8) - 2 * SCREENSHOT_MARGIN
        __QWINDOW_MAX_WIDTH: int = int(
            Utils.get_screen_resolution().width * 0.8) - 2 * SCREENSHOT_MARGIN
        __QWINDOW_UPPERBOUND_FRAME_WIDTH = 5
        __QWINDOW_UPPERBOUND_FRAME_HEIGHT = 35

        def _init_window(window_: QtW.QMainWindow):
            def _set_random_window_size():
                width, height = \
                    RandNumbersGeneration.generate_widget_size_values_for_grid(
                        tree_.root_node,
                        __QWINDOW_MAX_WIDTH,
                        __QWINDOW_MAX_HEIGHT)
                x, y = __QWINDOW_POSITION_COORD
                x += __QWINDOW_UPPERBOUND_FRAME_WIDTH
                y += __QWINDOW_UPPERBOUND_FRAME_HEIGHT
                window_.setGeometry(x, y, width, height)

            def _set_random_window_title():
                window_.setWindowTitle(
                    cls._rand_text_gen.gen_random_str_of_words(1, 3))

            def _init_central_widget():
                central_widget = QtW.QWidget()
                central_widget.setObjectName("centralWidget")

                if (random() > 0.1):
                    central_widget.setStyleSheet(
                        f"#centralWidget {{ border-image: url("
                        f"../../../resources/bg/"
                        f"{choice(Utils.get_background_names())}) "
                        f"0 0 0 0 stretch stretch; }}")
                central_widget.setLayout(layout)
                window_.setCentralWidget(central_widget)

            _init_central_widget()
            _set_random_window_size()
            _set_random_window_title()

        window = QtW.QMainWindow()
        _init_window(window)
        QtW.QApplication.setFont(generate_random_font())
        return window

    @classmethod
    def create_qline_edit(cls) -> QtW.QLineEdit:
        __QEDIT_ENABLED_PROB = 0.5
        __QEDIT_TEXT_FILLED_PROB = 0.5
        __QEDIT_FOCUS_PROB = 0.5

        line_edit = QtW.QLineEdit()
        palette = QtG.QPalette()
        palette.setColor(QtG.QPalette.ColorRole.PlaceholderText,
                         QtG.QColorConstants.DarkGray)
        line_edit.setPalette(palette)
        if random() < __QEDIT_TEXT_FILLED_PROB:
            line_edit.setText(
                cls._rand_text_gen.gen_random_str_of_words(1, 2))
        if random() < 1.0 - __QEDIT_ENABLED_PROB:
            line_edit.setEnabled(False)

        if random() < __QEDIT_FOCUS_PROB:
            line_edit.setFocus()

        line_edit.setSizePolicy(QtW.QSizePolicy.Minimum, QtW.QSizePolicy.Fixed)
        return line_edit

    @classmethod
    def create_qcheckable_line_edit(cls) -> QCheckableLineEdit:
        __QCHECKABLE_EDIT_ENABLED_PROB = 0.5
        __QCHECKABLE_EDIT_TEXT_FILLED_PROB = 0.5
        __QCHECKABLE_EDIT_CHECKED_PROB = 0.5
        __QCHECKABLE_EDIT_FOCUS_PROB = 0.5

        ch_line_edit = QCheckableLineEdit()
        palette = QtG.QPalette()
        palette.setColor(QtG.QPalette.ColorRole.PlaceholderText,
                         QtG.QColorConstants.DarkGray)
        ch_line_edit.setPalette(palette)
        if random() < __QCHECKABLE_EDIT_TEXT_FILLED_PROB:
            ch_line_edit.setText(
                cls._rand_text_gen.gen_random_str_of_words(1, 2))
        if random() < __QCHECKABLE_EDIT_CHECKED_PROB:
            ch_line_edit.checkbox.setChecked(True)
        if random() < 1.0 - __QCHECKABLE_EDIT_ENABLED_PROB:
            ch_line_edit.setEnabled(False)
        if random() < __QCHECKABLE_EDIT_FOCUS_PROB:
            ch_line_edit.setFocus()
        return ch_line_edit

    @classmethod
    def create_qbutton(cls) -> QtW.QPushButton:
        __QBUTTON_ENABLED_PROB = 0.5
        __QBUTTON_HAS_ICON_PROB = 0.5
        __QBUTTION_TEXT_PROB = 0.5
        __QBUTTION_FOCUS_PROB = 0.5

        button = QtW.QPushButton()
        button.setSizePolicy(QtW.QSizePolicy.Fixed, QtW.QSizePolicy.Fixed)
        if random() < __QBUTTON_HAS_ICON_PROB:
            p = QtG.QPixmap(str(choice(Utils.get_icon_paths())))
            button.setIcon(p)
        if random() < 1.0 - __QBUTTON_ENABLED_PROB:
            button.setEnabled(False)
        if random() < __QBUTTION_TEXT_PROB or button.icon().isNull():
            button.setText(
                cls._rand_text_gen.gen_random_str_of_words(1, 1))
        if random() < __QBUTTION_FOCUS_PROB:
            button.setFocus()

        return button

    @classmethod
    def create_qcombobox(cls) -> QtW.QComboBox:
        __QCOMBOBOX_ENABLED_PROB = 0.5
        __QCOMBOBOX_TEXT_FILLED_PROB = 1
        __QCOMBOBOX_FOCUS_PROB = 2

        cb_items = []
        if random() < __QCOMBOBOX_TEXT_FILLED_PROB:
            for i in range(randint(5, 30)):
                cb_items.append(
                    cls._rand_text_gen.gen_random_str_of_words(1, 1))
        else:
            cb_items.append("")
        combobox = QtW.QComboBox()
        combobox.addItems(cb_items)
        combobox.setCurrentIndex(0)
        if random() < 1.0 - __QCOMBOBOX_ENABLED_PROB:
            combobox.setEnabled(False)
        combobox.setSizePolicy(QtW.QSizePolicy.Minimum, QtW.QSizePolicy.Fixed)
        return combobox

    @classmethod
    def create_qcheckable_combobox(cls) -> QCheckableComboBox:
        __QCOMBOBOX_ENABLED_PROB = 0.5
        __QCOMBOBOX_TEXT_FILLED_PROB = 0.5
        __QCHECKBOX_CHECKED_PROB = 0.5
        __QCHECKBOX_FOCUS_PROB = 0.5

        text = cls._rand_text_gen.gen_random_str_of_words(1, 2) \
            if random() < __QCOMBOBOX_TEXT_FILLED_PROB else ""
        combobox = QCheckableComboBox()
        combobox.addItems([text])
        combobox.setCurrentIndex(0)
        if random() < __QCHECKBOX_CHECKED_PROB:
            combobox.checkbox.setChecked(True)
        if random() < 1.0 - __QCOMBOBOX_ENABLED_PROB:
            combobox.setEnabled(False)
        if random() < __QCHECKBOX_FOCUS_PROB:
            combobox.setFocus()
        return combobox

    @classmethod
    def create_qgroupbox(cls) -> QtW.QGroupBox:
        group_box = QtW.QGroupBox()
        alignment_types = [QtC.Qt.AlignLeft, QtC.Qt.AlignHCenter,
                           QtC.Qt.AlignHCenter]
        group_box.setAlignment(choice(alignment_types))
        return group_box

    @classmethod
    def create_qlist(cls) -> QtW.QListWidget:
        __QLIST_ITEMS_RANGE = 7, 25
        __QLIST_FOCUS_PROB = 0.5
        list_ = QtW.QListWidget()
        items_count = randint(*__QLIST_ITEMS_RANGE)
        list_.addItems(
            [cls._rand_text_gen.gen_random_str_of_words(1, 4)
             for _
             in range(items_count)])
        if random() < __QLIST_FOCUS_PROB:
            list_.setFocus()
            list_.setCurrentRow(randint(0, items_count))

        list_.setSizePolicy(QtW.QSizePolicy.MinimumExpanding,
                            QtW.QSizePolicy.MinimumExpanding)
        return list_

    @classmethod
    def create_qtextedit(cls) -> QtW.QTextEdit:
        TEXTEDIT_FOCUS_PROB = 0.5
        textedit = QtW.QTextEdit()
        textedit.insertHtml(cls._rand_text_gen.gen_random_html_doc())
        if random() < TEXTEDIT_FOCUS_PROB:
            textedit.setFocus()

        textedit.setSizePolicy(QtW.QSizePolicy.MinimumExpanding,
                               QtW.QSizePolicy.MinimumExpanding)
        return textedit

    @classmethod
    def create_qtreewidget(cls) -> QtW.QTreeWidget:
        __QTREEVIEW_COL_RANGE = 1, 3
        __QTREEVIEW_TOPLEVEL_ITEMS_COUNT_RANGE = 3, 5
        __QTREEVIEW_INNER_LEVEL_ITEMS_COUNT_RANGE = 2, 5

        __QTREEVIEW_EXPAND_TREE_ITEM_PROB = 0.6
        __QTREEVIEW_FOCUS_PROB = 0.5

        col_count = randint(*__QTREEVIEW_COL_RANGE)
        top_level_items_count = randint(
            *__QTREEVIEW_TOPLEVEL_ITEMS_COUNT_RANGE)
        top_level_items = []
        for i in range(top_level_items_count):
            item = QtW.QTreeWidgetItem()
            item.setText(0,
                         cls._rand_text_gen.gen_random_str_of_words(1, 1))
            for j in range(1, col_count):
                if j % 2 == 0:
                    t = cls._rand_text_gen.gen_random_str_of_words(1, 1)
                    item.setText(j, t)
                else:
                    t = RandNumbersGeneration \
                        .generate_random_line_of_numbers(1, 1, 1, 3)
                    item.setText(j, t)

            inner_level_items_count = randint(
                *__QTREEVIEW_INNER_LEVEL_ITEMS_COUNT_RANGE)
            inner_items = []
            for j in range(inner_level_items_count):
                inner_item = QtW.QTreeWidgetItem()
                inner_item.setText(
                    0, cls._rand_text_gen.gen_random_str_of_words(
                        1, 1))
                inner_items.append(inner_item)

            item.insertChildren(0, inner_items)
            top_level_items.append(item)

        qtreewidget = QtW.QTreeWidget()
        qtreewidget.setColumnCount(col_count)
        qtreewidget.insertTopLevelItems(0, top_level_items)
        labels = [cls._rand_text_gen.gen_random_str_of_words(1, 1)
                  for _ in range(col_count)]
        qtreewidget.setHeaderLabels(labels)
        if random() < __QTREEVIEW_EXPAND_TREE_ITEM_PROB:
            qtreewidget.topLevelItem(
                randint(0,
                        qtreewidget.topLevelItemCount() - 1)).setExpanded(True)
        if random() < __QTREEVIEW_FOCUS_PROB:
            item_n = randint(0, qtreewidget.topLevelItemCount() - 1)
            qtreewidget.topLevelItem(item_n).setSelected(True)

        qtreewidget.setSizePolicy(QtW.QSizePolicy.MinimumExpanding,
                                  QtW.QSizePolicy.MinimumExpanding)
        return qtreewidget

    @classmethod
    def create_qtabwidget(cls, main_widget: QtW.QWidget) -> QtW.QTabWidget:
        __QTAB_TAB_COUNT_RANGE = 2, 3

        tab_count = randint(*__QTAB_TAB_COUNT_RANGE)
        qtab = QtW.QTabWidget()
        qtab.addTab(main_widget,
                    cls._rand_text_gen.gen_random_str_of_words(1, 1))
        for _ in range(1, tab_count):
            qtab.addTab(QtW.QWidget(),
                        cls._rand_text_gen.gen_random_str_of_words(1, 1))

        return qtab

    @classmethod
    def create_qmenu(cls) -> QtW.QMenu:
        rand_phrase = cls._rand_text_gen.gen_random_str_of_words(1, 1)
        qmenu = QtW.QMenu(rand_phrase)
        return qmenu

    @classmethod
    def create_qstatusbar(cls):
        qstatusbar = QtW.QStatusBar()
        qstatusbar.showMessage(
            cls._rand_text_gen.gen_random_str_of_words(1, 4))
        return qstatusbar
