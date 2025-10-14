"""
Database query functions.
"""

from datetime import date
from enum import Enum
from typing import Final

import streamlit as st
from dateutil.rrule import MONTHLY, rrule
from polars import DataFrame

from database import DatabaseConnection


class SpinnerMessages(str, Enum):
    """
    Spinner messages for st.cache_data.
    """

    AVAILABLE_MONTHS = 'Atlasa datubāzē pieejamo laika periodu...'
    AVAILABLE_TR_TYPES = 'Atlasa pieejamos transporta veidus...'
    METRICS = 'Lejuplādē datus...'


# SQL query constants

SQL_AVAILABLE_MONTHS: Final[str] = """--sql
    select
        date(min(Laiks)) as min_date,
        date(max(Laiks)) as max_date
    from
        validacijas;
    """

SQL_AVAILABLE_TR_TYPES: Final[str] = """--sql
    select
        distinct TranspVeids
    from
        validacijas
    {where_clause}
    order by
        TranspVeids;
    """

SQL_TOTAL_RIDES: Final[str] = """--sql
    select
        count(*) as total_rides,
        round(count(*) / count(distinct date(Laiks)), 0) as avg_rides_per_day,
        date_trunc('month', Laiks) as moy
    from
        validacijas
    {where_clause}
    group by moy
    order by moy;
    """

SQL_PEAK_HOUR: Final[str] = """--sql
    with hs as
    (
        select range as hour from range(24)
    ),
    hd as
    (
        select
            count(*) as ride_count,
            hour(Laiks) as hour,
            count(distinct date(Laiks)) as distinct_days
        from
            validacijas
        {where_clause}
        group by hour
    )
    select
        hs.hour,
        coalesce(
            round((hd.ride_count / hd.distinct_days), 0),
            0
        ) as avg_rides_per_hour
    from
        hs
    left join
        hd on hs.hour = hd.hour
    order by hs.hour;
    """

SQL_POPULAR_ROUTES: Final[str] = """--sql
    select
        count(*) as 'Braucienu skaits',
        TMarsruts as 'Maršruts',
    from
        validacijas
    {where_clause}
    group by Tmarsruts
    order by count(*) desc
    limit 15;
    """


def _get_data_with_filters(
    db: DatabaseConnection,
    sql_query: str,
    up_to_date: date | None = None,
    date_range: tuple[date, date] | None = None,
    tr_types: list[str] | None = None,
) -> DataFrame:
    """
    Get data with optional date and transport type filtering.
    """
    where_clauses: list[str] = []
    params: dict[str, date | list[str]] = {}

    if date_range and len(date_range) == 2:
        start_date, end_date = date_range
        date_clause = """--sql
            Laiks >= $start_date and Laiks < $end_date::DATE + 1
            """
        where_clauses.append(date_clause)
        params['start_date'] = start_date
        params['end_date'] = end_date

    elif up_to_date:
        up_to_date_clause = """--sql
            Laiks < $up_to_date::DATE + 1
            """
        where_clauses.append(up_to_date_clause)
        params['up_to_date'] = up_to_date

    if tr_types:
        tr_clause = """--sql
            TranspVeids in $tr_types
            """
        where_clauses.append(tr_clause)
        params['tr_types'] = tr_types

    where_clause = 'where ' + ' and '.join(where_clauses) if where_clauses else ''

    query = sql_query.format(where_clause=where_clause)

    rel = db.get_relation(query, params)
    return rel.pl()


@st.cache_data(
    show_spinner=SpinnerMessages.AVAILABLE_MONTHS.value,
    show_time=True,
)
def get_available_months(_db: DatabaseConnection) -> list[date]:
    """
    Get available months from database.
    """
    rel_bounds = _db.get_relation(SQL_AVAILABLE_MONTHS)
    bounds = rel_bounds.fetchone()
    if bounds is None:
        raise ValueError('Datubāzē netika atrasta kolonna "Laiks".')
    start_date, end_date = bounds
    # Use the min and max value of column 'Laiks' to create a list of months inbetween
    res = list(
        rrule(
            freq=MONTHLY,
            dtstart=start_date,
            until=end_date,
        )
    )
    return res


@st.cache_data(
    show_spinner=SpinnerMessages.AVAILABLE_TR_TYPES.value,
    show_time=True,
)
def get_available_tr_types(
    _db: DatabaseConnection,
    date_range: tuple[date, date],
) -> DataFrame:
    """
    Get available transport types based on current filters.
    """
    return _get_data_with_filters(
        db=_db,
        sql_query=SQL_AVAILABLE_TR_TYPES,
        date_range=date_range,
    )


@st.cache_data(
    show_spinner=SpinnerMessages.METRICS.value,
    show_time=True,
)
def get_total_rides(
    _db: DatabaseConnection,
    up_to_date: date,
    tr_types: list[str] | None = None,
) -> DataFrame:
    """
    Get count of rides for each month up to selected month (excluding).
    """
    return _get_data_with_filters(
        db=_db,
        sql_query=SQL_TOTAL_RIDES,
        up_to_date=up_to_date,
        tr_types=tr_types,
    )


@st.cache_data(
    show_spinner=SpinnerMessages.METRICS.value,
    show_time=True,
)
def get_peak_hour(
    _db: DatabaseConnection,
    date_range: tuple[date, date],
    tr_types: list[str] | None = None,
) -> DataFrame:
    """
    Get the count for number of rides per each hour of day.
    """
    return _get_data_with_filters(
        db=_db,
        sql_query=SQL_PEAK_HOUR,
        date_range=date_range,
        tr_types=tr_types,
    )


@st.cache_data(
    show_spinner=SpinnerMessages.METRICS.value,
    show_time=True,
)
def get_popular_routes(
    _db: DatabaseConnection,
    date_range: tuple[date, date],
    tr_types: list[str] | None = None,
) -> DataFrame:
    """
    Get the list of routes ordered by count of rides.
    """
    return _get_data_with_filters(
        db=_db,
        sql_query=SQL_POPULAR_ROUTES,
        date_range=date_range,
        tr_types=tr_types,
    )
