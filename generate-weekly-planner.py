from sys import argv
from dataclasses import dataclass
from typing import List
from pathlib import Path
from typing import Dict

from datetime import date

from calendar import setfirstweekday
from calendar import Calendar
from calendar import HTMLCalendar
from calendar import SUNDAY
from calendar import month_name
from imgkit import from_string

from enum import Enum


"""
Okay, so let's get the show on the road. This program needs to do a few things:
- Identify the calendar days & break it down into weekly pages
- For each page, replace the template block with the latex for a calendar page
- For each month of the year, generate a .png small calendar
"""


class Month(Enum):
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
    def from_name(month_name: str):
        return Month[month_name.upper()]


@dataclass(order=True, frozen=True)
class WeeklyPage:
    """
    Used for latex template generation
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
    def first_ordinal(self):
        return self.to_page_header(self.first_day)

    @property
    def second_ordinal(self):
        return self.to_page_header(self.second_day)

    @property
    def third_ordinal(self):
        return self.to_page_header(self.third_day)

    @property
    def fourth_ordinal(self):
        return self.to_page_header(self.fourth_day)

    @property
    def fifth_ordinal(self):
        return self.to_page_header(self.fifth_day)

    @property
    def sixth_ordinal(self):
        return self.to_page_header(self.sixth_day)

    @property
    def seventh_ordinal(self):
        return self.to_page_header(self.seventh_day)

    @staticmethod
    def to_page_header(input_date: date) -> str:
        if input_date is None:
            return "Rest day"
        return f"{to_ordinal(input_date.day)} {input_date.strftime('%A')}"


class CustomHTMLCal(HTMLCalendar):
    cssclass_month_head = "text-center month-head"


class CalendarImage:
    """
    Used for the calendar image generation
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


def run(year: int) -> None:
    # TODO: move this to argparse
    args = {
        "show_frame": False,
        "year": year,
    }

    print(f"Generating calendar information for {year}")

    # Latex generation
    weekly_pages = generate_weekly_pages(year)
    generate_tex_weekly_planner(weekly_pages, args)

    # Calendar image generation
    calendars = generate_calendar_images(year, args)
    write_calendar_files(calendars)


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


def generate_tex_weekly_planner(weekly_pages: List[WeeklyPage], args: Dict):
    # Technically speaking a recursive writer would be more elegant, though for
    # v1 we're more concerned about getting it working end to end first. Also,
    # splitting IO writing and what to write would be an improvement so it can
    # be tested in a functional manner
    show_frame = args.get("show_frame", False)  # TODO move this to argparse
    primary_color = args.get("primary_color", "Plum")  # TODO move this to argparse
    year = args.get("year")
    # TODO: change what start date is(MONDAY, TUESDAY, WEDNESDAY, THURSDAY, FRIDAY, SATURDAY, SUNDAY) = range(7)
    with Path(f"weekly-planner-{year}.tex").open('w') as output_fp:
        write_header(output_fp, show_frame)
        write_weekly_pages(output_fp, weekly_pages, primary_color)
        write_tail(output_fp)


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


if __name__ == '__main__':
    # TODO: use argsparse later on to support multi-year generation support
    run(int(argv[1]))
