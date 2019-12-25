# General imports
from __future__ import annotations  # Enables self-referencing type hints, not needed in python 4.0+
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from datetime import date
from calendar import HTMLCalendar

# Values from https://en.wikibooks.org/wiki/LaTeX/Colors#The_68_standard_colors_known_to_dvips
valid_color_choices = {
    # Baseline LaTeX
    "black",
    "blue",
    "brown",
    "cyan",
    "darkgray",
    "gray",
    "green",
    "lightgray",
    "lime",
    "magenta",
    "olive",
    "orange",
    "pink",
    "purple",
    "red",
    "teal",
    "violet",
    "white",
    "yellow",

    # 68 dvips colors
    "Apricot",
    "Aquamarine",
    "Bittersweet",
    "Black",
    "Blue",
    "BlueGreen",
    "BlueViolet",
    "BrickRed",
    "Brown",
    "BurntOrange",
    "CadetBlue",
    "CarnationPink",
    "Cerulean",
    "CornflowerBlue",
    "Cyan",
    "Dandelion",
    "DarkOrchid",
    "Emerald",
    "ForestGreen",
    "Fuchsia",
    "Goldenrod",
    "Gray",
    "Green",
    "GreenYellow",
    "JungleGreen",
    "Lavender",
    "LimeGreen",
    "Magenta",
    "Mahogany",
    "Maroon",
    "Melon",
    "MidnightBlue",
    "Mulberry",
    "NavyBlue",
    "OliveGreen",
    "Orange",
    "OrangeRed",
    "Orchid",
    "Peach",
    "Periwinkle",
    "PineGreen",
    "Plum",
    "ProcessBlue",
    "Purple",
    "RawSienna",
    "Red",
    "RedOrange",
    "RedViolet",
    "Rhodamine",
    "RoyalBlue",
    "RoyalPurple",
    "RubineRed",
    "Salmon",
    "SeaGreen",
    "Sepia",
    "SkyBlue",
    "SpringGreen",
    "Tan",
    "TealBlue",
    "Thistle",
    "Turquoise",
    "Violet",
    "VioletRed",
    "White",
    "WildStrawberry",
    "Yellow",
    "YellowGreen",
    "YellowOrange",
}


class Month(Enum):
    """
    A nice helper utility, since there's a lot of different
    ways that month state representation occurs thanks to
    calls to other libraries, so we create this to refer
    to a single state, and just call the relevant presentation
    method that's required.
    """
    JANUARY = 1
    FEBRUARY = 2
    MARCH = 3
    APRIL = 4
    MAY = 5
    JUNE = 6
    JULY = 7
    AUGUST = 8
    SEPTEMBER = 9
    OCTOBER = 10
    NOVEMBER = 11
    DECEMBER = 12

    def title(self) -> str:
        return self.name.title()

    @staticmethod
    def from_name(current_month_name: str) -> Month:
        return Month[current_month_name.upper()]


@dataclass(order=True, frozen=True)
class WeeklyPage:
    """
    A class representing all data required to template
    a single page in the weekly planner
    """
    year: int
    month: Month

    first_day: date
    second_day: date
    third_day: date
    fourth_day: date
    fifth_day: date
    sixth_day: date
    seventh_day: date

    @property
    def calendar_image(self) -> str:
        return f"img/{self.year}-{self.month.title()}-calendar"

    @property
    def first_ordinal(self) -> str:
        return self.to_page_header(self.first_day)

    @property
    def second_ordinal(self) -> str:
        return self.to_page_header(self.second_day)

    @property
    def third_ordinal(self) -> str:
        return self.to_page_header(self.third_day)

    @property
    def fourth_ordinal(self) -> str:
        return self.to_page_header(self.fourth_day)

    @property
    def fifth_ordinal(self) -> str:
        return self.to_page_header(self.fifth_day)

    @property
    def sixth_ordinal(self) -> str:
        return self.to_page_header(self.sixth_day)

    @property
    def seventh_ordinal(self) -> str:
        return self.to_page_header(self.seventh_day)

    @staticmethod
    def to_page_header(input_date: date) -> str:
        if input_date is None:
            return "Rest day"
        return f"{to_ordinal(input_date.day)} {input_date.strftime('%A')}"


class CustomHTMLCal(HTMLCalendar):
    """
    An unfortunate byproduct of using the calendar library,
    where we need this whole particular class to enable accessing
    the title element of the calendar
    """
    cssclass_month_head = "month-head"


class CalendarImage:
    """
    Contains the actual data required to generate an image
    of the calendar via html
    """
    def __init__(self, year: int, month: Month, calendar: HTMLCalendar):
        self.year = year
        self.month = month
        self.calendar = calendar

    @property
    def path(self) -> Path:
        return Path(f"img/{self.year}-{self.month.title()}-calendar.png")

    @property
    def to_html(self) -> str:
        primary_color = "purple"  # TODO: inject in primary color into class and get rid of this
        primary_opposite_color = "white"  # TODO: inject in opposite primary color into class and get rid of this
        # TODO: download font locallt
        # TODO: Move the whole base template into a resource file
        raw_html = f"""
<!DOCTYPE html>
    <head>
        <style>
            /* Sets up a serif font in the same style as latex's default */
            /* TODO: download the font locally and add to file*/
            @font-face {{
                font-family: 'cmunserif'; src: url('http://mirrors.ctan.org/fonts/cm-unicode/fonts/otf/cmunrm.otf');
                font-weight: normal; font-style: normal;
            }}
            body {{
                font-family: 'cmunserif';
            }}

            .text-bold {{
              font-weight: bold;
            }}
            .month {{
                width: 610px;
            }}
            th {{
                color: {primary_color};
            }}
            .month-head {{
                background-color: {primary_color};
                color: {primary_opposite_color};
                text-align: center;
            }}
            th, td {{
                font-size: 50px;
                padding: 0;
                margin: 0;
                border: 0;
                text-align: center;
            }}
        </style>
        <title>Calendar</title>
    </head>
    <body>

        {self.calendar.formatmonth(self.year, self.month.value)}

    </body>
</html>
        """
        # All of this because the html calendar is a piece of shit
        raw_html = raw_html.replace("Mon", "M")
        raw_html = raw_html.replace("Tue", "T")
        raw_html = raw_html.replace("Wed", "W")
        raw_html = raw_html.replace("Thu", "T")
        raw_html = raw_html.replace("Fri", "F")
        raw_html = raw_html.replace("Sat", "S")
        raw_html = raw_html.replace("Sun", "S")
        return raw_html


"""
Helper functions
"""


def to_ordinal(n: int) -> str:
    """
    See https://stackoverflow.com/a/50992575.
    Convert an integer into its ordinal representation::

    make_ordinal(0)   => '0th'
    make_ordinal(3)   => '3rd'
    make_ordinal(122) => '122nd'
    make_ordinal(213) => '213th'
    """
    n = int(n)
    suffix = ['th', 'st', 'nd', 'rd', 'th'][min(n % 10, 4)]
    if 11 <= (n % 100) <= 13:
        suffix = 'th'
    return str(n) + suffix
