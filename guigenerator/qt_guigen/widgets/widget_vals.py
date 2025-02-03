from enum import Enum
from typing import Any, Dict


class WidgetContentName(Enum):
    TEXT = ("text", str)

    def __new__(cls, val, data_type):
        obj = object.__new__(cls)
        obj._value_ = val
        obj._data_type = data_type
        return obj

    @property
    def data_type(self):
        return self._data_type


class WidgetValsHolderBuilder:
    def __init__(self):
        self._widg_vals: Dict[WidgetContentName, Any] = {}

    def text(self, val: str = ""):
        name = WidgetContentName.TEXT
        self._widg_vals[name] = val
        return self

    def build(self) -> 'WidgetValsHolder':
        return WidgetValsHolder(self._widg_vals)


class WidgetValsHolder:
    def __init__(self, vals: Dict[WidgetContentName, Any] = None):
        if vals is None:
            vals = {}
        self._widg_vals: Dict[WidgetContentName, Any] = vals

        for value_name, value in self._widg_vals.items():
            if value_name.data_type is not type(value):
                raise RuntimeError("WidgetValueName data_type does not correspond to widgte_val type")

    def add_val(self, val_name: WidgetContentName, val: Any):
        if WidgetContentName.data_type is not type(val):
            raise RuntimeError("WidgetValueName data_type does not correspond to widgte_val type")
        self._widg_vals[val_name] = val

    def get_vals_dict(self) -> Dict[WidgetContentName, Any]:
        return self._widg_vals

    def get_attr(self, name: WidgetContentName) -> Any:
        return self._widg_vals[name]
