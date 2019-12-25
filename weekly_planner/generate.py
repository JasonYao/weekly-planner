# General imports
from sys import argv
from typing import List
from typing import Dict
from pathlib import Path

from datetime import date
from calendar import Calendar
from calendar import month_name

from argparse import ArgumentParser

# Vendor imports
from imgkit import from_string

# Project imports
from weekly_planner.models import Month
from weekly_planner.models import WeeklyPage
from weekly_planner.models import CalendarImage
from weekly_planner.models import CustomHTMLCal


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
    print(f"Generating calendar information for {year}")

    # Latex generation
    weekly_pages = generate_weekly_pages(year)
    tex_weekly_planner_path = generate_tex_weekly_planner(weekly_pages, args, year)

    # Calendar image generation
    calendars = generate_calendar_images(year, args)
    write_calendar_files(calendars)

    # Bi-weekly print view generation
    write_biweekly_view(year, tex_weekly_planner_path)


def generate_weekly_pages(year: int) -> List[WeeklyPage]:
    weekly_pages = []
    batch_size = 7
    calendar_dates = get_all_calendar_dates(year)
    for i in range(0, len(calendar_dates), batch_size):
        page_dates: List[date] = calendar_dates[i:i + batch_size]
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


def get_all_calendar_dates(year: int) -> List[date]:
    calendar_dates = []
    calendar = Calendar()
    # calendar.setfirstweekday(SUNDAY)
    for month in range(1, 13):
        for full_date in calendar.itermonthdates(year=year, month=month):
            calendar_dates.append(full_date)
    return calendar_dates


def generate_tex_weekly_planner(weekly_pages: List[WeeklyPage], args: Dict, year: int) -> Path:
    # Technically speaking a recursive writer would be more elegant, though for
    # v1 we're more concerned about getting it working end to end first. Also,
    # splitting IO writing and what to write would be an improvement so it can
    # be tested in a functional manner
    show_frame = args.get("show_frame")
    primary_color = args.get("primary_color")
    output_path = Path(f"weekly-planner-{year}.tex")
    with output_path.open('w') as output_fp:
        write_header(output_fp, show_frame)
        write_weekly_pages(output_fp, weekly_pages, primary_color)
        write_tail(output_fp)
    return output_path


def write_header(output_fp, show_frame: bool):
    output_fp.write(f"""
\\documentclass[a4paper]{{article}}

\\usepackage[{"showframe, " if show_frame else ""}portrait, margin=0.3in, top=0.5in]{{geometry}}
\\usepackage{{calendar}}

\\begin{{document}}
""")


def write_weekly_pages(output_fp, weekly_pages: List[WeeklyPage], primary_color: str):
    for weekly_page in weekly_pages:
        output_fp.write(f"""
  \\weeklyplanpage{{{primary_color},{weekly_page.year},{weekly_page.month.title()},{weekly_page.calendar_image},{weekly_page.first_ordinal},{weekly_page.second_ordinal},{weekly_page.third_ordinal},{weekly_page.fourth_ordinal},{weekly_page.fifth_ordinal},{weekly_page.sixth_ordinal},{weekly_page.seventh_ordinal}}}
""")


def write_tail(output_fp):
    output_fp.write("\\end{document}\n")


def generate_calendar_images(year: int, args: Dict) -> List[CalendarImage]:
    calendars = [generate_calendar_data(year - 1, Month.DECEMBER, args)]
    # Adds in the month of the year before

    for current_month_name in month_name:
        # Month names are 1-indexed with an empty string at 0 index
        if current_month_name == '':
            continue
        month = Month.from_name(current_month_name)
        calendars.append(generate_calendar_data(year, month, args))
    return calendars


def generate_calendar_data(year: int, month: Month, args: Dict) -> CalendarImage:
    calendar = CustomHTMLCal()  # TODO add in support for changing the start date
    # calendar.formatweekheader()
    # calendar_text = calendar.formatmonth(year, month)

    # img = Image.open("sample_in.jpg")
    # draw = ImageDraw.Draw(img)
    # # font = ImageFont.truetype(<font-file>, <font-size>)
    # font = ImageFont.truetype("sans-serif.ttf", 16)
    # # draw.text((x, y),"Sample Text",(r,g,b))
    # draw.text((0, 0), "Sample Text", (255, 255, 255), font=font)
    # img.save('sample-out.jpg')
    # img = Image.new('RGB', (60, 30), color='red')
    return CalendarImage(
        year=year,
        month=month,
        calendar=calendar,
    )


def write_calendar_files(calendars: List[CalendarImage]):
    options = {'width': 625, 'disable-smart-width': ''}
    for calendar in calendars:
        from_string(calendar.to_html, str(calendar.path), options=options)


def write_biweekly_view(year: int, tex_weekly_planner_path: Path):
    # TODO: move to resource fil
    template = f"""
%%
% 2019 Winter gift for my SO that loves a particular style
% of weekly planners, but is unable to find one exactly the
% way she wants.
%
% This project is completely tailored to the style that she
% prefers, so that she can just go to the website and click
% print.
%
% This is a wrapper class for a "Biweekly Print Version",
% where it shows two weeks on a single page in landscape.
%%
\\documentclass[twoside]{{article}}
\\usepackage{{pdfpages}}

\\begin{{document}}
\\pagestyle{{plain}}

\\includepdf[pages={{1-}},nup=1x2,landscape=true]{{{str(tex_weekly_planner_path).replace(".tex", ".pdf")}}}

\\end{{document}}
"""
    output_path = Path(f"biweekly-print-version-{year}.tex")
    with output_path.open('w') as output_fp:
        output_fp.write(template)
