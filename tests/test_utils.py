import decimal
from datetime import date

import pytest

from utils import (
    format_month_repr,
    format_month_repr_long,
    format_number,
    format_percent,
    last_day_of_month,
)


def test_format_number():
    """Test cases for format_number function"""
    assert format_number(1000) == '1\xa0tūkst.'
    assert format_number(1500) == '1,5\xa0tūkst.'
    assert format_number(1000000) == '1\xa0milj.'
    # Test edge cases
    assert format_number(0) == '0'
    assert format_number(1) == '1'
    assert format_number(999) == '999'
    # Test formatting of large numbers
    assert format_number(1234567) == '1,23\xa0milj.'
    assert format_number(1235467890) == '1,24\xa0mljrd.'
    # Test negative number formatting
    assert format_number(-1000) == '-1\xa0tūkst.'
    assert format_number(-1500) == '-1,5\xa0tūkst.'
    # Test that excatly 2 decimal places ar shown when needed
    assert format_number(1500) == '1,5\xa0tūkst.'
    assert format_number(1010) == '1,01\xa0tūkst.'
    assert format_number(1000) == '1\xa0tūkst.'


def test_last_day_of_month():
    """Test cases for last_day_of_month function"""
    assert last_day_of_month(date(2025, 12, 9)) == date(2025, 12, 31)
    # Test function works properly with a leap year
    assert last_day_of_month(date(2024, 2, 11)) == date(2024, 2, 29)
    # Test months that have 30 days
    assert last_day_of_month(date(2025, 4, 15)) == date(2025, 4, 30)
    # Test function works properly with a non leap year date
    assert last_day_of_month(date(2025, 2, 11)) == date(2025, 2, 28)
    # Test if function returns same date if last day is input
    assert last_day_of_month(date(2025, 12, 31)) == date(2025, 12, 31)
    # Test function returns last day of month if first day is input
    assert last_day_of_month(date(2025, 12, 1)) == date(2025, 12, 31)
    # Test function works properly with last day of year
    assert last_day_of_month(date(2025, 12, 31)) == date(2025, 12, 31)


def test_format_month_repr():
    """Test cases for format_month_repr function"""
    assert format_month_repr(date(2025, 1, 9)) == 'janvāris 2025'
    assert format_month_repr(date(2025, 2, 9)) == 'februāris 2025'
    assert format_month_repr(date(2025, 3, 9)) == 'marts 2025'
    assert format_month_repr(date(2025, 4, 9)) == 'aprīlis 2025'
    assert format_month_repr(date(2025, 5, 9)) == 'maijs 2025'
    assert format_month_repr(date(2025, 6, 9)) == 'jūnijs 2025'
    assert format_month_repr(date(2025, 7, 9)) == 'jūlijs 2025'
    assert format_month_repr(date(2025, 8, 9)) == 'augusts 2025'
    assert format_month_repr(date(2025, 9, 9)) == 'septembris 2025'
    assert format_month_repr(date(2025, 10, 9)) == 'oktobris 2025'
    assert format_month_repr(date(2025, 11, 9)) == 'novembris 2025'
    assert format_month_repr(date(2025, 12, 9)) == 'decembris 2025'
    # Test first and last day of month
    assert format_month_repr(date(2025, 1, 1)) == 'janvāris 2025'
    assert format_month_repr(date(2025, 1, 31)) == 'janvāris 2025'
    # Test leap year february returns same value as other years
    assert format_month_repr(date(2024, 2, 29)) == 'februāris 2024'
    assert format_month_repr(date(2025, 2, 1)) == 'februāris 2025'
    # Test past, present and future years
    assert format_month_repr(date(1999, 12, 31)) == 'decembris 1999'
    assert format_month_repr(date(2023, 5, 15)) == 'maijs 2023'
    assert format_month_repr(date(2050, 5, 15)) == 'maijs 2050'


def test_format_month_repr_long():
    """Test cases for format_month_repr_long function"""
    assert format_month_repr_long(date(2025, 1, 1)) == '2025. gada 1. janvāris'
    assert format_month_repr_long(date(2024, 2, 29)) == '2024. gada 29. februāris'
    assert format_month_repr_long(date(2025, 2, 28)) == '2025. gada 28. februāris'
    assert format_month_repr_long(date(2025, 3, 31)) == '2025. gada 31. marts'
    assert format_month_repr_long(date(1999, 4, 30)) == '1999. gada 30. aprīlis'
    assert format_month_repr_long(date(2025, 5, 9)) == '2025. gada 9. maijs'
    assert format_month_repr_long(date(2025, 5, 19)) == '2025. gada 19. maijs'
    assert format_month_repr_long(date(2050, 6, 15)) == '2050. gada 15. jūnijs'
    assert format_month_repr_long(date(2025, 7, 9)) == '2025. gada 9. jūlijs'
    assert format_month_repr_long(date(2025, 8, 10)) == '2025. gada 10. augusts'
    assert format_month_repr_long(date(2025, 9, 19)) == '2025. gada 19. septembris'
    assert format_month_repr_long(date(2025, 10, 3)) == '2025. gada 3. oktobris'
    assert format_month_repr_long(date(2025, 11, 20)) == '2025. gada 20. novembris'
    assert format_month_repr_long(date(2025, 12, 31)) == '2025. gada 31. decembris'
    with pytest.raises(ValueError):
        format_month_repr_long(date(2025, 12, 32))


def test_format_percent():
    """Test cases for format_percent function"""
    # Basic percentages
    assert format_percent(0.5) == '50,00 %'
    assert format_percent(0.123) == '12,30 %'

    # Edge cases
    assert format_percent(0.0) == '0,00 %'
    assert format_percent(1.0) == '100,00 %'
    assert format_percent(1.3) == '130,00 %'

    # Negative percentages
    assert format_percent(-0.25) == '-25,00 %'

    # Rounding behavior
    assert format_percent(0.1234) == '12,34 %'
    assert format_percent(0.1235) == '12,35 %'
    assert format_percent(0.12346) == '12,35 %'

    # Extreme values
    assert format_percent(0.00001) == '0,00 %'
    assert format_percent(0.99999) == '100,00 %'

    # Invalid input
    with pytest.raises(decimal.InvalidOperation):
        format_percent('not_a_number')  # type: ignore
    with pytest.raises(decimal.InvalidOperation):
        format_percent(None)  # type: ignore
