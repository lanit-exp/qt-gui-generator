import sys
from pathlib import Path
from random import randint, choice
from typing import List, Tuple, Union
import matplotlib.pyplot as plt

from PySide6 import QtWidgets as QtW
from PySide6 import QtCore as QtC

from guigenerator.dto.tree_dto import NodeDto, TreeDto
from guigenerator.qt_guigen.config import PyQtGuiGenConfig
from guigenerator.qt_guigen.export_data import ExportAttrDataFactory, \
    ExportWidgetContentFactory, ExportGeomDataFactory
from guigenerator.qt_guigen.screenshot import ScreenshotHandler, Screenshot
from guigenerator.qt_guigen.widgets import GeometryOutputDataFormat, \
    AttributesDataFormat, ValuesDataFormat
from guigenerator.qt_guigen.widgets.widget_dict import WidgetDataDict, \
    WidgetDataDictFactory
from guigenerator.qt_guigen.widgets.widgetobject.wo_abc import \
    WidgetObjectMixin, ContainerWidgetObjectMixin
from guigenerator.qt_guigen.widgets.widgetobject.wo_concrete import \
    MenuItemWidget
from guigenerator.qt_guigen.widgets.widgetobject.wo_factory import \
    WidgetObjectFactory
from guigenerator.tree_guigen.gui_tree_gen import TreeGeneration
from guigenerator.utils import Utils


class QtDatasetGeneration:
    __config = PyQtGuiGenConfig.get_section("DatasetGeneration")

    DATASET_SIZE = __config.get_int("dataset_size")
    EMPTY_SCREENSHOTS_RATIO = __config.get_float("empty_screenshots_ratio")
    DATASET_ITEM_NUMBER_OF_WIDGETS = randint(__config.get_int("n_min_widgets"),
                                             __config.get_int("n_max_widgets"))
    STYLESHEETS = __config.get_list("stylesheets")

    TREE_DESCRIPTION_PATH = Utils.PROJ_ROOT_DIR / __config.get_path(
        "tree_description_path")
    GENERATED_TREE_PATH = Utils.PROJ_ROOT_DIR / __config.get_path(
        "generated_tree_path")
    EXPORT_WIDGET_GEOM_PATH = __config.get_path(
        "export_widget_geometries_dir_path")
    EXPORT_WIDGET_ATTR_PATH = __config.get_path(
        "export_widget_attributes_dir_path")
    EXPORT_WIDGET_CONTENT_PATH = __config.get_path(
        "export_widget_content_dir_path")

    GENERATED_TREE_PATH.parent.mkdir(parents=True, exist_ok=True)
    EXPORT_WIDGET_GEOM_PATH.mkdir(parents=True, exist_ok=True)
    EXPORT_WIDGET_ATTR_PATH.mkdir(parents=True, exist_ok=True)
    EXPORT_WIDGET_CONTENT_PATH.mkdir(parents=True, exist_ok=True)

    yolo_widget_data = None
    coco_widget_data = None
    widgets_counter_list = []

    @classmethod
    def generate(cls):
        yolo_widget_data_list: List[Tuple[Screenshot, 'WidgetDataDict']] = []
        coco_widget_data_list: List[Tuple[Screenshot, 'WidgetDataDict']] = []

        QtW.QApplication(sys.argv)

        for item_num in range(cls.DATASET_SIZE):
            print(f"------------------ {item_num + 1}")

            is_main_widget_invisible = item_num >= cls.DATASET_SIZE \
                                       - cls.get_nmb_of_empty_widgets()
            root_widget_object = cls._generate_application_instance(
                cls.DATASET_ITEM_NUMBER_OF_WIDGETS)

            def _do_while_taking_screenshot():
                cls.yolo_widget_data = WidgetDataDictFactory.create_dict(
                    root_widget_object,
                    GeometryOutputDataFormat.YOLO)
                cls.coco_widget_data = WidgetDataDictFactory.create_dict(
                    root_widget_object,
                    GeometryOutputDataFormat.COCO)

            if is_main_widget_invisible:
                for child_wo in root_widget_object.get_children():
                    child_wo.widget.setVisible(False)
                root_widget_object.clear_menubar()

            screenshot = ScreenshotHandler.take_main_screenshot(
                root_widget_object,
                _do_while_taking_screenshot)
            if is_main_widget_invisible:
                cls.yolo_widget_data = WidgetDataDictFactory.create_empty_dict(
                    root_widget_object)
                cls.coco_widget_data = WidgetDataDictFactory.create_empty_dict(
                    root_widget_object)

            yolo_widget_data_list.append(
                (screenshot, cls.yolo_widget_data))
            coco_widget_data_list.append((screenshot,
                                          cls.coco_widget_data))
            ScreenshotHandler.extract_widget_screenshots(
                screenshot,
                root_widget_object,
                cls.yolo_widget_data.get_geometry_items())

            cls.widgets_counter_list \
                .append(cls.yolo_widget_data.get_geometry_distrib())

        yolo_geom_exporter = ExportGeomDataFactory.get_exporter(
            GeometryOutputDataFormat.YOLO,
            cls.EXPORT_WIDGET_GEOM_PATH)
        yolo_geom_exporter.export(yolo_widget_data_list)

        coco_geom_exporter = ExportGeomDataFactory.get_exporter(
            GeometryOutputDataFormat.COCO,
            cls.EXPORT_WIDGET_GEOM_PATH)
        coco_geom_exporter.export(coco_widget_data_list)

        attr_exporter \
            = ExportAttrDataFactory.get_exporter(AttributesDataFormat.CSV,
                                                 cls.EXPORT_WIDGET_ATTR_PATH)
        attr_exporter.export(yolo_widget_data_list)

        widget_content_exporter \
            = ExportWidgetContentFactory.get_exporter(ValuesDataFormat.CSV,
                                                      cls.EXPORT_WIDGET_CONTENT_PATH)
        widget_content_exporter.export(yolo_widget_data_list)

        cls.print_widgets_distribution()

    @classmethod
    def print_widgets_distribution(cls):
        print("***------------***")
        widget_distrib = {}
        total = 0
        for d in cls.widgets_counter_list:
            for name, count in d.items():
                if name in PyQtGuiGenConfig.get_section(
                        "GeometryDataExport").get_list("widget_except_list"):
                    continue
                if name not in widget_distrib.keys():
                    widget_distrib[name] = 0
                widget_distrib[name] += count
                total += count
        if "Button" not in widget_distrib.keys():
            widget_distrib["Button"] = 0
        if "HorScrollBar" not in widget_distrib.keys():
            widget_distrib["HorScrollBar"] = 0
        if "VertScrollBar" not in widget_distrib.keys():
            widget_distrib["VertScrollBar"] = 0
        if "ScrollBarButton" not in widget_distrib.keys():
            widget_distrib["ScrollBarButton"] = 0
        if "MenuItem" not in widget_distrib.keys():
            widget_distrib["MenuItem"] = 0
        widget_distrib["ScrollBar"] = widget_distrib["HorScrollBar"] + \
                                      widget_distrib["VertScrollBar"]
        widget_distrib.pop("HorScrollBar")
        widget_distrib.pop("VertScrollBar")

        widget_distrib["Button"] += widget_distrib["ScrollBarButton"]
        widget_distrib["Button"] += widget_distrib["MenuItem"]
        widget_distrib.pop("ScrollBarButton")
        widget_distrib.pop("MenuItem")
        labels = []
        counts = []
        if total != 0:
            for name, widget_count in widget_distrib.items():
                percentage = widget_count / total
                labels.append(name)
                counts.append(widget_count)
                print(f"name={name}; percent={percentage}")


        plt.figure(figsize=(12, 5))
        plt.bar(labels, counts)
        plt.show()

    @classmethod
    def set_stylesheet_or_leave_default(cls, app):
        ssh_file = cls.choose_stylesheet()
        # with open(ssh_file, "r") as fh:
        #     app.setStyleSheet(fh.read())

    @classmethod
    def choose_stylesheet(cls) -> Path:
        stylesheets_dir = Utils.get_stylesheets_dir_path()
        stylesheet = stylesheets_dir / choice(cls.STYLESHEETS)
        print(f"Current stylesheet is {stylesheet.name}")
        return stylesheet

    # method order inside the function is important because widgets'
    # geometry in qt initialized only after
    # gui exec which happens in take_main_screenshot function
    @classmethod
    def _generate_application_instance(cls, widget_nmbs: int):
        TreeGeneration.generate_tree(widget_nmbs,
                                     input_path=cls.TREE_DESCRIPTION_PATH.__str__(),
                                     output_path=cls.GENERATED_TREE_PATH.__str__())
        gui_root_widget_object = QtGuiGeneration.generate(
            cls.GENERATED_TREE_PATH.__str__())
        app = QtW.QApplication.instance()
        cls.set_stylesheet_or_leave_default(app)
        return gui_root_widget_object

    @classmethod
    def get_nmb_of_empty_widgets(cls) -> int:
        return int(cls.DATASET_SIZE * cls.EMPTY_SCREENSHOTS_RATIO)


class QtGuiGeneration:
    @classmethod
    def generate(cls, tree_path: str) -> Union[
        ContainerWidgetObjectMixin, WidgetObjectMixin]:
        root_node: NodeDto = Utils.read_from_json(tree_path,
                                                  lambda d: NodeDto(**d))
        tree: TreeDto = TreeDto(root_node)
        root_widget_object = cls._create_gui_from_tree(tree)
        return root_widget_object

    @classmethod
    def _create_gui_from_tree(cls,
                              tree_: TreeDto) -> ContainerWidgetObjectMixin:
        root_widget_object: ContainerWidgetObjectMixin \
            = WidgetObjectFactory.create_root_widget_object(
            tree_.root_node.name, tree_)
        MenuItemWidget.reset_id_count()

        cls._create_children(tree_.root_node, root_widget_object)
        return root_widget_object

    @classmethod
    def _create_children(cls, parent_tree_node: NodeDto,
                         parent_widget_object: Union[
                             WidgetObjectMixin, ContainerWidgetObjectMixin]):
        for child_tree_node in parent_tree_node.children:
            child_widget_object = cls._create_child(child_tree_node,
                                                    parent_widget_object)

            cls._create_children(child_tree_node, child_widget_object)

    @classmethod
    def _create_child(cls, child_tree_node: NodeDto,
                      parent_widget_object: Union[
                          WidgetObjectMixin, ContainerWidgetObjectMixin]):
        child_widget_object = WidgetObjectFactory.create_widget_object(
            child_tree_node.name)

        parent_widget_object.add_child(child_widget_object)
        return child_widget_object


if __name__ == "__main__":
    QtDatasetGeneration.generate()
