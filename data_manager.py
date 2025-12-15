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

SQL_RIDES_PER_DAY: Final[str] = """--sql
    select
        count(*) as total_rides,
        date_trunc('day', Laiks) as dom
    from
        validacijas
    {where_clause}
    group by dom
    order by dom;
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

SQL_TR_DISTRIBUTION: Final[str] = """--sql
    select
        count(*) as 'Braucienu skaits',
        TranspVeids as 'Transporta veids'
    from
        validacijas
    {where_clause}
    group by TranspVeids
    order by count(*) desc;
    """

SQL_PEAK_DAY: Final[str] = """--sql
    with dow as
    (
        select
            isodow(Laiks) as dow,
            round(count(*) / count(distinct date(Laiks)), 0) as avg_rides_per_day
        from
            validacijas
        {where_clause}
        group by isodow(Laiks)
    )
    select
        case dow
            when 1 then 'Pirmdiena'
            when 2 then 'Otrdiena'
            when 3 then 'Trešdiena'
            when 4 then 'Ceturtdiena'
            when 5 then 'Piektdiena'
            when 6 then 'Sestdiena'
            when 7 then 'Svētdiena'
        end as 'Nedēļas diena',
        avg_rides_per_day as 'Braucieni vidēji dienā'
    from
        dow
    order by dow;
    """

SQL_ROUTE_DENSITY: Final[str] = """--sql
    select
        TMarsruts as 'Maršruts',
        round(count(*) / count(distinct GarNr), 0) as 'Vidējais braucienu skaits'
    from
        validacijas
    {where_clause}
    group by TMarsruts
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
    # Normalize the dates to start of month

    start_date = date(start_date.year, start_date.month, 1)
    end_date = date(end_date.year, end_date.month, 1)

    # Use the min and max value of column 'Laiks' to create a list of months inbetween
    res: list[date] = []
    for i in rrule(
        freq=MONTHLY,
        dtstart=start_date,
        until=end_date,
    ):
        res.append(i.date())
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


@st.cache_data(show_spinner=SpinnerMessages.METRICS.value, show_time=True)
def get_rides_per_day(
    _db: DatabaseConnection,
    date_range: tuple[date, date],
    tr_types: list[str] | None = None,
) -> DataFrame:
    """
    Get count of rides for each day of the selected month.
    """
    return _get_data_with_filters(
        db=_db,
        sql_query=SQL_RIDES_PER_DAY,
        date_range=date_range,
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


@st.cache_data(
    show_spinner=SpinnerMessages.METRICS.value,
    show_time=True,
)
def get_tr_distribution(
    _db: DatabaseConnection,
    date_range: tuple[date, date],
    tr_types: list[str] | None = None,
) -> DataFrame:
    """
    Get the distribution of rides between the transport types.
    """
    return _get_data_with_filters(
        db=_db,
        sql_query=SQL_TR_DISTRIBUTION,
        date_range=date_range,
        tr_types=tr_types,
    )


@st.cache_data(
    show_spinner=SpinnerMessages.METRICS.value,
    show_time=True,
)
def get_peak_day(
    _db: DatabaseConnection,
    date_range: tuple[date, date],
    tr_types: list[str] | None = None,
) -> DataFrame:
    """
    Get the average count of rides per each day of week in month.
    """
    return _get_data_with_filters(
        db=_db,
        sql_query=SQL_PEAK_DAY,
        date_range=date_range,
        tr_types=tr_types,
    )


@st.cache_data(
    show_spinner=SpinnerMessages.METRICS.value,
    show_time=True,
)
def get_route_density(
    _db: DatabaseConnection,
    date_range: tuple[date, date],
    tr_types: list[str] | None = None,
) -> DataFrame:
    """
    Get ridership density (rides per vehicle) for top routes.
    """
    return _get_data_with_filters(
        db=_db,
        sql_query=SQL_ROUTE_DENSITY,
        date_range=date_range,
        tr_types=tr_types,
    )
