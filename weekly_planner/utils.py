# General imports
from dataclasses import dataclass
from pkg_resources import resource_stream
from json import load as json_load
from enum import Enum


@dataclass(frozen=True, order=True)
class ColorWrapper:
    name: str
    hexcode: str


# Values from https://en.wikibooks.org/wiki/LaTeX/Colors#The_68_standard_colors_known_to_dvips
with resource_stream("weekly_planner.resources.utils", "colors.json") as colors_fp:
    __colors = json_load(colors_fp)

__named_colors = []
for __color in __colors:
    name: str = __color.get("name")
    hexcode: str = __color.get("hexcode")
    access_name = name.replace(" ", "_").replace("(", "_").replace(")", "_").upper()

    __named_colors.append((access_name, ColorWrapper(name=name, hexcode=hexcode),))
Color = Enum("Color", __named_colors)


def normal_name(self):
    return self.value.name


def hexcode(self):
    return self.value.hexcode


def from_name(self, access_name: str):
    return Color[access_name]


Color.normal_name = normal_name
Color.hexcode = hexcode
Color.from_name = from_name
