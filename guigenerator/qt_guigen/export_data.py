import copy
import csv
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Dict, Tuple, ItemsView

from guigenerator.dto.coco_dto import LicenseDto, InfoDto, CategoryDto, \
    ImageDto, AnnotationDto, CocoDto, LabelInputDto, LabelInputLinksDto
from guigenerator.qt_guigen.config import PyQtGuiGenConfig
from guigenerator.qt_guigen.screenshot import Screenshot
from guigenerator.qt_guigen.widgets import GeometryOutputDataFormat, \
    AttributesDataFormat, ValuesDataFormat
from guigenerator.qt_guigen.widgets.widget_dict import WidgetDataDict
from guigenerator.qt_guigen.widgets.widget_geometry import WidgetGeometry
from guigenerator.qt_guigen.widgets.widget_names import WidgetNames
from guigenerator.utils import Utils


class ExportGeomDataFactory:
    @classmethod
    def get_exporter(cls, data_format: GeometryOutputDataFormat,
                     export_path: Path) -> 'GeomDataExporter':
        if data_format == GeometryOutputDataFormat.YOLO:
            return YoloGeomDataExporter(export_path)
        else:
            return CocoGeomDataExporter(export_path)


class GeomDataExporter(ABC):
    __geometry_config = PyQtGuiGenConfig.get_section("GeometryDataExport")
    __attr_config = PyQtGuiGenConfig.get_section("AttributeDataExport")
    _widget_name_to_index_dict: Dict[str, int] = None

    def __init__(self, dir_path: Path):
        self._dir_path: Path = dir_path

    @property
    def dir_path(self) -> Path:
        return self._dir_path

    @abstractmethod
    def export(self,
               image_geometry_list: List[Tuple[Screenshot, WidgetDataDict]]):
        pass

    @classmethod
    def _get_acceptable_widget_names_for_geometry(cls) -> List[str]:
        except_list = cls.__geometry_config.get_list('widget_except_list')
        return [name for name in WidgetNames.get_possible_enum_names() if
                name not in except_list]

    @classmethod
    def _get_acceptable_widget_names_for_attr(cls) -> List[str]:
        acceptable_list = cls.__attr_config.get_list("widgets_for_export")
        return acceptable_list

    @classmethod
    def _get_widget_name_to_index_dict(cls) -> Dict[str, int]:
        if cls._widget_name_to_index_dict is None:
            cls._widget_name_to_index_dict = {}
            for index, name in enumerate(
                    cls._get_acceptable_widget_names_for_geometry()):
                cls._widget_name_to_index_dict[name] = index

        return cls._widget_name_to_index_dict

    def _create_file(self, filename: str, extension: str, text: str):
        filename: Path = Path(filename)
        file_path = self.dir_path / filename.with_suffix(extension)
        Utils.write_to_file(file_path, text)

    def __add_quality_to_filename(self, filename: str) -> Path:
        splited_filename = filename.split("-q")
        if len(splited_filename) > 1:
            return Path(splited_filename[0] + Path(splited_filename[1]).suffix)
        else:
            return Path(filename)


class YoloGeomDataExporter(GeomDataExporter):
    __config = PyQtGuiGenConfig.get_section("YoloGeometryDataExport")

    LABEL_FILE_NAME = __config.get("label_file_name")
    LABEL_EXTENSION = __config.get("label_extension")
    GEOMETRY_EXTENSION = __config.get("geometry_files_extension")

    def __init__(self, dir_path: Path):
        super(YoloGeomDataExporter, self).__init__(dir_path)

    def export(self,
               image_geometry_list: List[Tuple[Screenshot, WidgetDataDict]]):
        label_text = self._create_label_text()
        self._create_file(self.LABEL_FILE_NAME, self.LABEL_EXTENSION,
                          label_text)

        for screenshot, data_item in image_geometry_list:
            geom_text = self._get_geometry_text(data_item.get_geometry_items())
            self._create_file(screenshot.filestem, self.GEOMETRY_EXTENSION,
                              geom_text)

    def _get_geometry_text(self, widget_geometry: ItemsView[
        str, dict[int, WidgetGeometry]]):
        result_text: List[str] = []
        for widget_name, widget_geometries_dict in widget_geometry:
            result_text += \
                self._create_geometry_text_for_all_widgets_of_this_name(
                    widget_name, list(widget_geometries_dict.values()))
        return ''.join(result_text)

    def _create_geometry_text_for_all_widgets_of_this_name(self,
                                                           widget_container_name,
                                                           widget_geometries_list) \
            -> List[str]:
        name_to_index: Dict[str, int] = self._get_widget_name_to_index_dict()
        text_list: List[str] = []
        for widget_geometry in widget_geometries_list:
            if widget_container_name in name_to_index.keys():
                line = f'{name_to_index[widget_container_name]} ' \
                       f'{widget_geometry}\n'
                text_list.append(line)
        return text_list

    def _create_label_text(self):
        return '\n'.join(
            self._get_acceptable_widget_names_for_geometry()) + '\n'


class CocoGeomDataExporter(GeomDataExporter, ABC):
    __config = PyQtGuiGenConfig.get_section("CocoGeometryDataExport")

    GEOMETRY_FILE_NAME = __config.get("coco_file_name")
    GEOMETRY_EXTENSION = __config.get("coco_file_extension")

    def __init__(self, dir_path: Path):
        super(CocoGeomDataExporter, self).__init__(dir_path)

    def export(self,
               image_geometry_list: List[Tuple[Screenshot, WidgetDataDict]]):
        license_ = LicenseDto()
        info = InfoDto()

        category_dict = {}
        category_list = []
        for i, category_name in enumerate(
                self._get_acceptable_widget_names_for_geometry()):
            category_dict[category_name] = i + 1
            category_list.append(CategoryDto(i + 1, category_name))

        image_list = []
        annotation_list = []
        label_input_list = []
        annotation_id = 1
        for image_id, image_geometry_item in enumerate(image_geometry_list,
                                                       start=1):
            screenshot, widget_data_dict = image_geometry_item

            original_widget_ids_label_input_link = \
                widget_data_dict.get_label_input_link_ids()
            result_widget_ids_label_input_link = copy.deepcopy(
                widget_data_dict.get_label_input_link_ids())

            image_list.append(
                ImageDto(image_id, screenshot.width, screenshot.height,
                         screenshot.filename))
            for widget_name, geometry_attr_dict in \
                    widget_data_dict.get_attr_geometry_items_for_coco():

                if widget_name not in \
                        self._get_acceptable_widget_names_for_geometry():
                    continue

                for id_, value in geometry_attr_dict.items():
                    for index, label_input in enumerate(
                            original_widget_ids_label_input_link):

                        if label_input.have_id(id_):
                            if widget_name == "Label":
                                result_widget_ids_label_input_link[
                                    index].replace_label_id(annotation_id)
                                print("Label")
                                print(id_, annotation_id)
                            else:
                                result_widget_ids_label_input_link[
                                    index].replace_input_id(annotation_id)
                                print("input")
                                print(id_, annotation_id)
                            break

                    geometry, attr_list = value
                    bbox = [geometry.x, geometry.y, geometry.width,
                            geometry.height]
                    category_id = category_dict[widget_name]
                    annotDto = AnnotationDto(annotation_id, image_id,
                                             category_id, bbox)
                    if attr_list and widget_name in \
                            self._get_acceptable_widget_names_for_attr():
                        annotDto.attributes \
                            .update({attr.name.fancy_name: attr.state_name
                                     for attr in attr_list})
                    annotation_list.append(annotDto)
                    annotation_id += 1

                print(original_widget_ids_label_input_link)
                print(result_widget_ids_label_input_link)

            label_input_list.extend([LabelInputDto(image_id,
                                                   label_input.label_id,
                                                   label_input.input_id)
                                     for label_input in
                                     result_widget_ids_label_input_link])

        coco_dto = CocoDto([license_], info, category_list, image_list,
                           annotation_list)

        filename = self.GEOMETRY_FILE_NAME + '.json'
        Utils.write_to_json(coco_dto, str(self.dir_path / filename))

        filename = "label_input_link.json"
        label_input_dto = LabelInputLinksDto(label_input_list)
        Utils.write_to_json(label_input_dto, str(self.dir_path / filename))


class ExportAttrDataFactory:
    @classmethod
    def get_exporter(cls, data_format: AttributesDataFormat,
                     export_path: Path) -> 'AttrDataExporter':
        if data_format == AttributesDataFormat.CSV:
            return CSVAttrDataExporter(export_path)
        else:
            raise RuntimeError("No such otp format")


class AttrDataExporter(ABC):
    __config = PyQtGuiGenConfig.get_section("AttributeDataExport")
    _widget_name_to_index_dict: Dict[str, int] = None

    def __init__(self, dir_path: Path):
        self._dir_path: Path = dir_path
        self._widgets_for_export = self.__config.get_list("widgets_for_export")

    @property
    def dir_path(self) -> Path:
        return self._dir_path

    @abstractmethod
    def export(self,
               image_geometry_list: List[Tuple[Screenshot, WidgetDataDict]]):
        pass


class CSVAttrDataExporter(AttrDataExporter):
    FILE_EXTENSION = ".csv"
    FILENAME_PREFIX = "metadata_"

    def __init__(self, dir_path: Path):
        super().__init__(dir_path)

    def export(self,
               image_geometry_list: List[Tuple[Screenshot, WidgetDataDict]]):
        for screenshot, data_item in image_geometry_list:
            for widget_name, attr_dict in data_item.get_attr_items():
                if widget_name in self._widgets_for_export:
                    metadata_file_path = self.dir_path / Path(
                        self.FILENAME_PREFIX + widget_name +
                        self.FILE_EXTENSION)
                    out_lines = []
                    for widget_id, list_of_attr in attr_dict.items():
                        main_screenshot_name = Path(screenshot.filename)
                        widget_screenshot_name = widget_name + '-' + \
                                                 main_screenshot_name.stem + \
                                                 '-' + str(
                            widget_id) \
                                                 + main_screenshot_name.suffix
                        out_lines.append(
                            [widget_screenshot_name] + [attr.state_name for
                                                        attr in list_of_attr])

                    with open(metadata_file_path, 'a', newline='') as csvfile:
                        writer = csv.writer(csvfile, delimiter=',',
                                            quotechar='|',
                                            quoting=csv.QUOTE_MINIMAL)
                        writer.writerows(out_lines)


class ExportWidgetContentFactory:
    @classmethod
    def get_exporter(cls, data_format: ValuesDataFormat,
                     export_path: Path) -> 'WidgetContentExporter':
        if data_format == ValuesDataFormat.CSV:
            return CSVWidgetContentExporter(export_path)
        else:
            raise RuntimeError("No such otp format")


class WidgetContentExporter(ABC):
    __config = PyQtGuiGenConfig.get_section("WidgetValuesDataExport")
    _widget_name_to_index_dict: Dict[str, int] = None

    def __init__(self, dir_path: Path):
        self._dir_path: Path = dir_path
        self._widgets_for_export = self.__config.get_list("widgets_for_export")

    @property
    def dir_path(self) -> Path:
        return self._dir_path

    @abstractmethod
    def export(self,
               image_geometry_list: List[Tuple[Screenshot, WidgetDataDict]]):
        pass


class CSVWidgetContentExporter(WidgetContentExporter):
    FILE_EXTENSION = ".csv"
    FILENAME_PREFIX = "widget_vals_"

    def __init__(self, dir_path: Path):
        super().__init__(dir_path)

    def export(self,
               image_geometry_list: List[Tuple[Screenshot, WidgetDataDict]]):
        for screenshot, data_item in image_geometry_list:
            for widget_name, widget_value_dict_by_widget_id in \
                    data_item.get_vals_items():
                if widget_name in self._widgets_for_export:
                    widget_val_file_path = self.dir_path / Path(
                        self.FILENAME_PREFIX + widget_name
                        + self.FILE_EXTENSION)
                    out_lines = []
                    for widget_id, widget_value_dict in \
                            widget_value_dict_by_widget_id.items():
                        main_screenshot_name = Path(screenshot.filename)
                        widget_screenshot_name = widget_name + '-' + \
                                                 main_screenshot_name.stem + \
                                                 '-' + str(
                            widget_id) \
                                                 + main_screenshot_name.suffix
                        for widget_value_name, widget_value in \
                                widget_value_dict.items():
                            out_lines.append([widget_screenshot_name] + [
                                widget_value.__str__()])

                    with open(widget_val_file_path, 'a',
                              newline='') as csvfile:
                        writer = csv.writer(csvfile, delimiter=',',
                                            quotechar='|',
                                            quoting=csv.QUOTE_NONE,
                                            escapechar='\\')
                        writer.writerows(out_lines)
