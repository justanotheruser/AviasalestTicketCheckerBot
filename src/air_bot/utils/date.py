import copy
import re
from datetime import datetime
from random import shuffle
from typing import Optional, Any


def get_date_examples() -> str:
    return "январь,  01,  01.2023,  01 2023,  01 23"


class DateReader:
    def __init__(self) -> None:
        self.strptime_patterns = [
            "%m %Y",
            "%m.%Y",
            "%m-%Y",
            "%Y %m",
            "%Y.%m",
            "%Y-%m",
            "%d.%m.%y",
            "%d-%m-%y",
            "%d %m %y",
            "%d.%m.%Y",
            "%d-%m-%Y",
            "%d %m %Y",
            "%y.%m.%d",
            "%y-%m-%d",
            "%y %m %d",
            "%Y.%m.%d",
            "%Y-%m-%d",
            "%Y %m %d",
        ]

    def read_date(self, user_date: str) -> Optional[str]:
        parsers = [parse_two_digits_couples]
        for pattern in self.strptime_patterns:
            parsers.append(make_parser(pattern))
        for parser in parsers:
            year, month, day = parser(user_date)
            if year:
                if day:
                    return f"{year}-{month:02d}-{day:02d}"
                return f"{year}-{month:02d}"
        return None

    def get_examples(self, n: int = 3) -> list[str]:
        date_formats = copy.copy(self.strptime_patterns)
        shuffle(date_formats)
        return [
            datetime.strftime(datetime.now(), date_format)
            for date_format in date_formats[:n]
        ]


def make_parser(strptime_pattern: str) -> Any:
    def parser(user_date: str) -> tuple[Optional[int], Optional[int], Optional[int]]:
        try:
            date = datetime.strptime(user_date, strptime_pattern)
        except ValueError:
            return None, None, None
        if "%d" in strptime_pattern:
            return date.year, date.month, date.day
        return date.year, date.month, None

    return parser


def parse_two_digits_couples(
    user_date: str,
) -> tuple[Optional[int], Optional[int], Optional[int]]:
    year, month, day = None, None, None
    two_numbers_regex = re.compile(r"(\d\d)(\.|-|\s)(\d\d)")
    match = two_numbers_regex.fullmatch(user_date)
    if match:
        first_digits_couple, second_digits_couple = int(match.group(1)), int(
            match.group(3)
        )
        if second_digits_couple >= 23:
            month = first_digits_couple
            year = 2000 + second_digits_couple
        elif second_digits_couple <= 12:
            day = first_digits_couple
            month = second_digits_couple
            year = datetime.now().year
    return year, month, day
