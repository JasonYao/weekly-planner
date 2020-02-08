# General imports
from typing import List
from typing import Dict
from pathlib import Path

from datetime import date
from calendar import Calendar
from calendar import month_name

# Vendor imports
from imgkit import from_string

# Project imports
from weekly_planner.models import DayOfTheWeek
from weekly_planner.models import Month
from weekly_planner.models import WeeklyPage
from weekly_planner.models import CalendarImage
from weekly_planner.models import CustomHTMLCal
from weekly_planner.models import load_resource_file

from weekly_planner.utils import Color

"""
Okay, so let's get the show on the road. This program needs to do a few things:
- Identify the calendar days & break it down into weekly pages
- For each page, replace the template block with the latex for a calendar page
- For each month of the year, generate a .png small calendar
"""


def run(args: Dict) -> None:
    for year in args.get("years"):
        generate_weekly_planner_for_year(args, year)


def generate_weekly_planner_for_year(args: Dict, year: int):
    weekly_planner_tex_path = Path(f"weekly-planner-{year}.tex")
    weekly_planner_pdf_path = Path(f"weekly-planner-{year}.pdf")
    biweekly_print_view_tex_path = Path(f"biweekly-print-version-{year}.tex")

    # Latex generation
    weekly_pages = generate_weekly_pages(args, year)
    weekly_planner_tex = generate_weekly_planner_tex(weekly_pages, args)
    write_to_file(weekly_planner_tex, weekly_planner_tex_path)

    # Calendar image generation
    calendars = generate_calendar_images(year, args)
    write_calendar_files(calendars)

    # Bi-weekly print view generation
    biweekly_print_view_tex = generate_biweekly_print_view_tex(weekly_planner_pdf_path)
    write_to_file(biweekly_print_view_tex, biweekly_print_view_tex_path)


def generate_weekly_pages(args: Dict, year: int) -> List[WeeklyPage]:
    planner_start_day: DayOfTheWeek = args.get("planner_start_day")
    weekly_pages = []
    batch_size = 7
    calendar_dates = get_all_calendar_dates(year, planner_start_day)

    seen_page_dates = set()
    for i in range(0, len(calendar_dates), batch_size):
        page_dates: List[date] = calendar_dates[i:i + batch_size]

        # Lazy fix to avoid having to add in logic surrounding the end week of a month
        if tuple(page_dates) in seen_page_dates:
            continue

        seen_page_dates.add(tuple(page_dates))
        number_of_dates_on_page = len(page_dates)
        weekly_pages.append(WeeklyPage(
            year=page_dates[0].year,
            month=month_name[page_dates[0].month],
            first_day=page_dates[0] if number_of_dates_on_page > 0 else None,
            second_day=page_dates[1] if number_of_dates_on_page > 1 else None,
            third_day=page_dates[2] if number_of_dates_on_page > 2 else None,
            fourth_day=page_dates[3] if number_of_dates_on_page > 3 else None,
            fifth_day=page_dates[4] if number_of_dates_on_page > 4 else None,
            sixth_day=page_dates[5] if number_of_dates_on_page > 5 else None,
            seventh_day=page_dates[6] if number_of_dates_on_page > 6 else None
        ))
    return weekly_pages


def get_all_calendar_dates(year: int, planner_start_day: DayOfTheWeek) -> List[date]:
    calendar_dates = []
    calendar = Calendar()
    calendar.setfirstweekday(planner_start_day.value)
    for month in range(1, 13):
        for full_date in calendar.itermonthdates(year=year, month=month):
            calendar_dates.append(full_date)
    return calendar_dates


def generate_weekly_planner_tex(weekly_pages: List[WeeklyPage], args: Dict) -> str:
    show_frame: bool = args.get("show_frame")
    primary_color: Color = args.get("primary_color")
    secondary_color: Color = args.get("secondary_color")
    weekly_planner_page_template = load_resource_file("weekly-planner-page-template.tex")
    weekly_planner_template = load_resource_file("weekly-planner-template.tex")

    templated_pages = '\n'.join([template_page(weekly_planner_page_template, weekly_page, primary_color, secondary_color) for weekly_page in weekly_pages])

    templated_weekly_planner = weekly_planner_template.replace("{{show_frame}}", "showframe, " if show_frame else "")
    templated_weekly_planner = templated_weekly_planner.replace("{{pages}}", templated_pages)
    return templated_weekly_planner


def template_page(template: str, page_data: WeeklyPage, primary_color: Color, secondary_color: Color) -> str:
    templated_string = template.replace("{{primary_color}}", primary_color.hexcode().replace("#", ""))
    templated_string = templated_string.replace("{{secondary_color}}", secondary_color.hexcode().replace("#", ""))
    templated_string = templated_string.replace("{{year}}", str(page_data.year))
    templated_string = templated_string.replace("{{month}}", page_data.month.title())
    templated_string = templated_string.replace("{{calendar_image}}", page_data.calendar_image)
    templated_string = templated_string.replace("{{first_ordinal}}", page_data.first_ordinal)
    templated_string = templated_string.replace("{{second_ordinal}}", page_data.second_ordinal)
    templated_string = templated_string.replace("{{third_ordinal}}", page_data.third_ordinal)
    templated_string = templated_string.replace("{{fourth_ordinal}}", page_data.fourth_ordinal)
    templated_string = templated_string.replace("{{fifth_ordinal}}", page_data.fifth_ordinal)
    templated_string = templated_string.replace("{{sixth_ordinal}}", page_data.sixth_ordinal)
    templated_string = templated_string.replace("{{seventh_ordinal}}", page_data.seventh_ordinal)
    return templated_string


def write_to_file(data: str, output_path: Path) -> None:
    with output_path.open('w') as output_fp:
        output_fp.write(data)


def generate_calendar_images(year: int, args: Dict) -> List[CalendarImage]:
    # Adds in the month of the year before in case we need to reference it
    calendars = [generate_calendar_data(year - 1, Month.DECEMBER, args)]

    for month in Month:
        calendars.append(generate_calendar_data(year, month, args))
    return calendars


def generate_calendar_data(year: int, month: Month, args: Dict) -> CalendarImage:
    start_day: DayOfTheWeek = args.get("calendar_start_day")
    primary_color: Color = args.get("primary_color")
    secondary_color: Color = args.get("secondary_color")

    calendar = CustomHTMLCal()
    calendar.setfirstweekday(start_day.value)
    return CalendarImage(
        year=year,
        month=month,
        calendar=calendar,
        primary_color=primary_color,
        secondary_color=secondary_color,
    )


def write_calendar_files(calendars: List[CalendarImage]):
    options = {
        'width': 625,
    }
    for calendar in calendars:
        from_string(calendar.to_html, str(calendar.path), options=options)


def generate_biweekly_print_view_tex(biweekly_planner_path: Path):
    biweekly_planner_template = load_resource_file("biweekly-print-version-template.tex")
    templated_biweekly_planner_tex = biweekly_planner_template.replace("{{weekly_planner_path}}", str(biweekly_planner_path))
    return templated_biweekly_planner_tex
