"""
Utility functions.
"""

from calendar import monthrange
from datetime import date

from babel import Locale
from babel.dates import format_date
from babel.numbers import format_compact_decimal, format_decimal

_locale = Locale('lv')


def format_number(value: int) -> str:
    """
    Format number with Latvian locale.
    """
    return format_compact_decimal(value, locale=_locale, fraction_digits=2)


def last_day_of_month(start_day: date) -> date:
    """
    Return the last day of the start_day month.
    """
    return date(
        start_day.year, start_day.month, monthrange(start_day.year, start_day.month)[1]
    )


def format_month_repr(date: date) -> str:
    """
    Format date to show month and year with Latvian locale.
    """
    return format_date(date, format='MMMM YYYY', locale=_locale)


def format_percent(i: float) -> str:
    """
    Format number to display percentage.
    """
    return format_decimal(i, format='#.00 %', locale=_locale)
