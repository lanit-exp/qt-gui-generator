import configparser
from pathlib import Path
from typing import List, Dict

from guigenerator.dto.widget_description_dto import WidgetDescriptionDto
from guigenerator.utils import Utils


class PyQtGuiGenConfig:
    __CONFIG_PATH = Utils.PROJ_ROOT_DIR / "config/guigenerator_config.ini"
    __config: configparser.RawConfigParser = configparser.ConfigParser()
    __is_read = False

    @classmethod
    def get_section(cls, section: str) -> 'PyQtGuiGenConfigSectionProxy':
        if not cls.__is_read:
            cls._read_config()
        return PyQtGuiGenConfigSectionProxy(cls.__config[section])

    @classmethod
    def _read_config(cls):
        cls.__config.read(Path(cls.__CONFIG_PATH))
        cls.__is_read = True


class PyQtGuiGenConfigSectionProxy:
    USE_ROOT_PREFIX_WITH_PATHS_OPTION = "use_proj_root_prefix_with_paths"

    def __init__(self, section_proxy: configparser.SectionProxy):
        self.__section_proxy = section_proxy

    def get_int(self, option: str) -> int:
        return self.__section_proxy.getint(option)

    def get_float(self, option: str) -> float:
        return self.__section_proxy.getfloat(option)

    def get_boolean(self, option: str) -> bool:
        return self.__section_proxy.getboolean(option)

    def get(self, option: str) -> str:
        return self.__section_proxy.get(option)

    def get_path(self, option: str) -> Path:
        option_path = Path(self.__section_proxy.get(option))
        use_root = self.get_boolean(self.USE_ROOT_PREFIX_WITH_PATHS_OPTION)
        return Path(Utils.PROJ_ROOT_DIR) / option_path \
            if use_root else option_path

    def get_list(self, option: str) -> List[str]:
        return list(map(lambda s: s.strip(), self.get(option).split(',')))


class WidgetObjectDescrConfig:
    __CONFIG_PATH = Utils.PROJ_ROOT_DIR / Path("config/tree_widgets_description.json")
    __descriptions: Dict[str, 'WidgetObjectDescription'] = {}
    __is_read = False

    @classmethod
    def get_widget_object_description(cls, name: str) -> 'WidgetObjectDescription':
        if not cls.__is_read:
            cls.__read_widget_object_description()

        if name in cls.__descriptions.keys():
            return cls.__descriptions[name]
        else:
            return WidgetObjectDescription("No_name", False)

    @classmethod
    def __read_widget_object_description(cls):
        cls.__descriptions = cls.__read_descriptions_dict()
        cls.__is_read = True

    @classmethod
    def __read_descriptions_dict(cls) -> Dict[str, 'WidgetObjectDescription']:
        widgets_desc_dto = Utils.read_from_json(cls.__CONFIG_PATH, object_hook_=lambda d: WidgetDescriptionDto(**d))
        widgets_desc = [cls.__get_widget_object_description_from_dto(dto) for dto in widgets_desc_dto]
        return {wd.name: wd for wd in widgets_desc}

    @classmethod
    def __get_widget_object_description_from_dto(cls, dto: WidgetDescriptionDto):
        return WidgetObjectDescription(dto.name, dto.container, dto.min_width, dto.min_height, dto.accept_list,
                                       dto.central_widget_child, dto.padding)


class WidgetObjectDescription:
    def __init__(self, _name: str, _container: bool, _min_width: int = 0, _min_height: int = 0,
                 _accept_list: List[str] = None, _central_widget_child: bool = False, _padding: int = -1):
        if _accept_list is None:
            _accept_list = []
        self._name: str = _name
        self._container: bool = _container
        self._accept_list: List[str] = _accept_list
        self._min_width: int = _min_width
        self._min_height: int = _min_height
        self._central_widget_child = _central_widget_child
        if _padding == -1:
            _padding = PyQtGuiGenConfig.get_section("WidgetGeometry").get_int("default_widget_bbox_padding")
        self._padding = _padding

    @property
    def name(self) -> str:
        return self._name

    @property
    def container(self) -> bool:
        return self._container

    @property
    def accept_list(self) -> List[str]:
        return self._accept_list

    @property
    def min_width(self) -> int:
        return self._min_width

    @property
    def min_height(self) -> int:
        return self._min_height

    @property
    def central_widget_child(self) -> bool:
        return self._central_widget_child

    @property
    def padding(self) -> int:
        return self._padding
