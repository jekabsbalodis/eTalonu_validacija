"""
Functions for st.session_state management.
"""

from datetime import date
from enum import Enum

from streamlit.runtime.state.session_state_proxy import SessionStateProxy

from data_manager import (
    get_available_months,
    get_available_tr_types,
    get_peak_day,
    get_peak_hour,
    get_popular_routes,
    get_rides_per_day,
    get_route_density,
    get_total_rides,
    get_tr_distribution,
)
from database import DatabaseConnection
from utils import last_day_of_month


class StateKeys(str, Enum):
    """
    Values for the st.session_state keys.
    """

    AVAILABLE_MONTHS = 'available_months'
    SELECTED_MONTH = 'selected_month'
    AVAILABLE_TR_TYPES = 'available_tr_types'
    SELECTED_TR_TYPES = 'selected_tr_types'
    METRICS = 'metrics'


class MetricsKeys(str, Enum):
    """
    Values for the st.session_state.metrics dict of DataFrames.
    """

    TOTAL_RIDES = 'total_rides'
    PEAK_HOUR = 'peak_hour'
    POPULAR_ROUTES = 'popular_routes'
    TR_DISTRIBUTION = 'tr_distribution'
    PEAK_DAY = 'peak_day'
    ROUTE_DENSITY = 'route_density'
    RIDES_PER_DAY = 'rides_per_day'


def init_state(db: DatabaseConnection, session_state: SessionStateProxy) -> None:
    """
    Initializes necessary st.session_state objects.
    """

    # Available months
    if StateKeys.AVAILABLE_MONTHS not in session_state:
        session_state[StateKeys.AVAILABLE_MONTHS] = get_available_months(db)

    # Default month
    default_month = session_state[StateKeys.AVAILABLE_MONTHS][-1]
    if StateKeys.SELECTED_MONTH not in session_state:
        session_state[StateKeys.SELECTED_MONTH] = default_month

    # Available transport types
    min_date: date = date(default_month.year, default_month.month, 1)
    max_date: date = last_day_of_month(min_date)
    if StateKeys.AVAILABLE_TR_TYPES not in session_state:
        update_available_tr_types(
            db=db,
            session_state=session_state,
            date_range=(min_date, max_date),
        )
        session_state[StateKeys.SELECTED_TR_TYPES] = session_state[
            StateKeys.AVAILABLE_TR_TYPES
        ]
    # Metrics for initial app load
    if StateKeys.METRICS not in session_state:
        session_state[StateKeys.METRICS] = {}

        tr_types: list[str] = session_state[StateKeys.AVAILABLE_TR_TYPES]

        update_metrics(
            db=db,
            session_state=session_state,
            date_range=(min_date, max_date),
            tr_types=tr_types,
        )


def update_available_tr_types(
    db: DatabaseConnection,
    session_state: SessionStateProxy,
    date_range: tuple[date, date],
) -> None:
    """
    Update available transport types based on current selections.
    """

    available_tr_types = get_available_tr_types(
        db,
        date_range=date_range,
    )

    session_state[StateKeys.AVAILABLE_TR_TYPES] = available_tr_types.get_column(
        'TranspVeids'
    ).to_list()


def update_metrics(
    db: DatabaseConnection,
    session_state: SessionStateProxy,
    date_range: tuple[date, date],
    tr_types: list[str],
) -> None:
    """
    Update all metrics in session state based on current selections.
    """
    min_date, max_date = date_range

    session_state[StateKeys.METRICS][MetricsKeys.TOTAL_RIDES] = get_total_rides(
        _db=db,
        up_to_date=max_date,
        tr_types=tr_types,
    )

    session_state[StateKeys.METRICS][MetricsKeys.RIDES_PER_DAY] = get_rides_per_day(
        _db=db,
        date_range=date_range,
        tr_types=tr_types,
    )

    session_state[StateKeys.METRICS][MetricsKeys.PEAK_HOUR] = get_peak_hour(
        _db=db,
        date_range=date_range,
        tr_types=tr_types,
    )

    session_state[StateKeys.METRICS][MetricsKeys.POPULAR_ROUTES] = get_popular_routes(
        _db=db,
        date_range=date_range,
        tr_types=tr_types,
    )

    session_state[StateKeys.METRICS][MetricsKeys.TR_DISTRIBUTION] = get_tr_distribution(
        _db=db,
        date_range=date_range,
        tr_types=tr_types,
    )

    session_state[StateKeys.METRICS][MetricsKeys.PEAK_DAY] = get_peak_day(
        _db=db,
        date_range=date_range,
        tr_types=tr_types,
    )

    session_state[StateKeys.METRICS][MetricsKeys.ROUTE_DENSITY] = get_route_density(
        _db=db,
        date_range=date_range,
        tr_types=tr_types,
    )
