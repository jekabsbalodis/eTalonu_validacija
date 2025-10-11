"""
Utility functions.
"""

from calendar import monthrange
from datetime import date

from babel import Locale
from babel.numbers import format_compact_decimal
from babel.dates import formar_date

_locale = Locale('lv')


def format_number(value: int, **kwargs) -> str:
    """
    Format number with Latvian locale.
    """
    return format_compact_decimal(value, locale=_locale, **kwargs)


def last_day_of_month(start_day: date) -> date:
    """
    Return the last day of the start_day month.
    """
    return date(
        start_day.year, start_day.month, monthrange(start_day.year, start_day.month)[1]
    )

def format_date(date: date) -> str:
    """
    Format date to show month and year with Latvian locale
    """
    return format_date(date, format='MMMM YYYY', locale = _locale)