"""
Functions for st.session_state management.
"""

from datetime import date
from enum import Enum

from streamlit.runtime.state.session_state_proxy import SessionStateProxy

from data_manager import (
    get_available_months,
    get_available_tr_types,
    get_total_rides,
    get_total_rides_up_to_month,
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
    TOTAL_RIDES_UP_TO_MONTH = 'total_rides_up_to_month'


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
        available_tr_types = get_available_tr_types(db, date_range=(min_date, max_date))
        session_state[StateKeys.AVAILABLE_TR_TYPES] = (
            available_tr_types.to_series().to_list()
        )
        session_state[StateKeys.SELECTED_TR_TYPES] = (
            available_tr_types.to_series().to_list()
        )

    # Metrics for initial app load
    if StateKeys.METRICS not in session_state:
        session_state[StateKeys.METRICS] = {}

        session_state[StateKeys.METRICS][MetricsKeys.TOTAL_RIDES] = get_total_rides(
            _db=db,
            date_range=(min_date, max_date),
        )
        session_state[StateKeys.METRICS][MetricsKeys.TOTAL_RIDES_UP_TO_MONTH] = (
            get_total_rides_up_to_month(
                _db=db,
                up_to_date=min_date,
            )
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

    session_state[StateKeys.AVAILABLE_TR_TYPES] = (
        available_tr_types.to_series().to_list()
    )
