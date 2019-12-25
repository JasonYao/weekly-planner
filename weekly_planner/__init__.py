# General imports
from datetime import datetime
from typing import List
from typing import Dict
from argparse import ArgumentParser

# Project imports
from .generate import run
from .models import DayOfTheWeek
from .models import valid_color_choices
from .models import valid_day_starts
from .utils import Color

##
# Exposes the argument parsing and expected usage
##


def start(args: List) -> None:
    parsed_arguments = parse_arguments(args)
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
    parser.add_argument("-p", "--primary-color", help="The main color for the title and calendar", default=Color.PLUM, type=lambda color: Color.from_name(color), choices={color.name for color in Color}, metavar='COLOR_NAME')
    parser.add_argument("-sc", "--secondary-color", help="The accent color (read: text color) for the title and calendar", default=Color.WHITE, type=lambda color: Color.from_name(color), choices={color.name for color in Color}, metavar='COLOR_NAME')
    parser.add_argument("-sd", "--start-day", help="The day that the weekly planner should start on (defaults to monday)", default=DayOfTheWeek.MONDAY, choices=valid_day_starts, type=lambda day: DayOfTheWeek.from_name(day))

    return parser
