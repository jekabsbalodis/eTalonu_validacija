"""
Information about available months and their data URLs.
"""

import calendar
import datetime
from dataclasses import dataclass
from typing import Final

MonthMap = dict[tuple[int, int], str]


@dataclass(frozen=True, slots=True)
class MonthData:
    """
    Holds month-to-URL dictionary with lookup functionality.
    """

    data: MonthMap

    def url(self, year: int, month: int) -> str | None:
        """
        Get the data URL for a specific year and month.

        Returns None if no data exists for the given year/month.
        """

        return self.data.get((year, month))

    def min_month(self) -> tuple[int, int] | None:
        """
        Get the minimum month (year, month) for which data is available.

        Returns None if no data is available.
        """
        if not self.data:
            return None
        return min(self.data.keys())

    def max_month(self) -> tuple[int, int] | None:
        """
        Get the maximum month (year, month) for which data is available.

        Returns None if no data is available.
        """
        if not self.data:
            return None
        return max(self.data.keys())

    def date_bounds(self) -> tuple[datetime.date, datetime.date] | None:
        """
        Get a tuple for the first day of first month that has data and
        for the last day of last month that has data.AVAILABLE_MONTHS

        Returns None if no data is available.
        """
        if not self.data:
            return None

        min_m: tuple[int, int] = self.min_month()
        max_m: tuple[int, int] = self.max_month()

        min_date = datetime.date(min_m[0], min_m[1], 1)

        last_day: int = calendar.monthrange(max_m[0], max_m[1])[1]
        max_date = datetime.date(max_m[0], max_m[1], last_day)

        return min_date, max_date


RESOURCE_PART: Final[str] = (
    'https://data.gov.lv/dati/dataset/638852d1-f4db-4484-9bca-0b80b84f2001/resource'
)


AVAILABLE_MONTHS: Final[MonthMap] = {
    (2025, 8): (
        f'{RESOURCE_PART}/330b4dac-ba2a-4553-8d14-9a0d9fb9b0f4/'
        'download/validacijudati08_2025.zip'
    ),
    (2025, 7): (
        f'{RESOURCE_PART}/710398c7-a673-492a-98a4-939d3707abb7/'
        'download/validacijudati07_2025.zip'
    ),
}

available_months: MonthData = MonthData(AVAILABLE_MONTHS)
