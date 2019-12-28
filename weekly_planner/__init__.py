# General imports
from datetime import datetime
from typing import List
from typing import Dict
from argparse import ArgumentParser

# Project imports
from .generate import run
from .models import DayOfTheWeek
from .utils import Color

##
# Exposes the argument parsing and expected usage
##

VALID_DAY_STARTS = set(DayOfTheWeek)
VALID_COLOR_CHOICES = set(Color)


def start(args: List) -> None:
    parsed_arguments = parse_arguments(args)
    if parsed_arguments.get("show_colors"):
        show_colors()
    else:
        run(parsed_arguments)


def parse_arguments(args: List) -> Dict:
    parser = get_parser()
    parsed_args = parser.parse_args(args)
    return vars(parsed_args)


def get_parser() -> ArgumentParser:
    parser = ArgumentParser(
        prog=f"weekly_planner run",
        description="Generates one or more weekly planners",
    )

    logging_parser_group = parser.add_mutually_exclusive_group()
    logging_parser_group.add_argument("-v", "--verbose", help="Enables more verbose logging", action="store_true")
    logging_parser_group.add_argument("-q", "--quiet",
                                      help="Squelches the default logging (still outputs to stderr upon failures)",
                                      action="store_true")

    parser.add_argument("-d", "--debug", help="Turns on some useful debugging capabilities such as showing latex margins", action='store_true')

    parser.add_argument("years", help="The years that we should generate the weekly planner for", nargs="*", type=int, default=[datetime.now().year])
    parser.add_argument("-p", "--primary-color", help="The main color for the title and calendar", default=Color.PLUM, type=lambda color: Color.from_name(color), choices=VALID_COLOR_CHOICES, metavar='COLOR_NAME')
    parser.add_argument("-s", "--secondary-color", help="The accent color (read: text color) for the title and calendar", default=Color.WHITE, type=lambda color: Color.from_name(color), choices=VALID_COLOR_CHOICES, metavar='COLOR_NAME')
    parser.add_argument("-r", "--planner-start-day", help="The day that the weekly planner should start on (defaults to monday)", default=DayOfTheWeek.MONDAY, choices=VALID_DAY_STARTS, type=lambda day: DayOfTheWeek.from_name(day))
    parser.add_argument("-c", "--calendar-start-day", help="The day that the mini calendar should start on (defaults to sunday)", default=DayOfTheWeek.SUNDAY, choices=VALID_DAY_STARTS, type=lambda day: DayOfTheWeek.from_name(day))

    parser.add_argument("-g", "--show-colors", help="Displays the supported colors and their associated hexcode value", action='store_true')
    return parser


def show_colors() -> None:
    for color in Color:
        rgb = color.rgb()
        print("{0:50}: {1} {2}".format(f"{color.name}", f"{color.hexcode()}", get_example_color_block(rgb[0], rgb[1], rgb[2])))


def get_example_color_block(red: int, green: int, blue: int) -> str:
    # See here for more info: https://stackoverflow.com/a/45782972
    # Can't use an f-string here since we need the backslash
    message = "   "
    return '\033[48;2;{};{};{}m{}\033[0m'.format(red, green, blue, message)
