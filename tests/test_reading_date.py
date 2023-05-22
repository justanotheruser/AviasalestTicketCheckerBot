from air_bot.utils.date import DateReader


def get_date(year, month, day=None):
    if day:
        return f"{year}-{month:02d}-{day:02d}"
    return f"{year}-{month:02d}"


def test_simple_formats():
    date_reader = DateReader()
    user_input2expected_result = {
        "01.06": get_date(2023, 6, 1),
        "01.24": get_date(2024, 1),
        "01-24": get_date(2024, 1),
        "06.2023": get_date(2023, 6),
        "06 2024": get_date(2024, 6),
        "07-2023": get_date(2023, 7),
        "11 10 2023": get_date(2023, 10, 11),
        "01-08-2024": get_date(2024, 8, 1),
        "01.09.2025": get_date(2025, 9, 1),
        "2025.09.01": get_date(2025, 9, 1),
        "2024-08-01": get_date(2024, 8, 1),
        "2023 10 11": get_date(2023, 10, 11),
        "2023-06": get_date(2023, 6),
    }
    for user_input, expected_result in user_input2expected_result.items():
        assert date_reader.read_date(user_input) == expected_result
