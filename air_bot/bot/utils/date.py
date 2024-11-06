import copy
import re
from datetime import datetime
from random import shuffle
from typing import Any, List, Optional, Tuple


class DateReader:
    strptime_patterns = [
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

    def __init__(self) -> None:
        self.parsers = [parse_two_digits_couples]
        for pattern in self.strptime_patterns:
            self.parsers.append(make_parser(pattern))

    def read_date(self, user_date: str) -> Optional[str]:
        for parser in self.parsers:
            year, month, day = parser(user_date)
            if year:
                if day:
                    return "{year}-{month:0>2}-{day:0>2}".format(year=year, month=month, day=day)
                return "{year}-{month:0>2}".format(year=year, month=month)
        return None

    @classmethod
    def get_examples(cls, n: int = 3) -> List[str]:
        date_formats = copy.copy(cls.strptime_patterns)
        shuffle(date_formats)
        return [
            datetime.strftime(datetime.now(), date_format)
            for date_format in date_formats[:n]
        ]


def make_parser(strptime_pattern: str) -> Any:
    def parser(user_date: str) -> Tuple[Optional[int], Optional[int], Optional[int]]:
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
) -> Tuple[Optional[int], Optional[int], Optional[int]]:
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


date_reader = DateReader()
