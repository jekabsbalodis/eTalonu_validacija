"""
Callback functions to pass to streamlit widgets.
"""

from datetime import date

import streamlit as st
from streamlit.runtime.state.session_state_proxy import SessionStateProxy

from data_manager import get_total_rides, get_total_rides_up_to_month
from database import db
from state_manager import MetricsKeys, StateKeys, update_available_tr_types
from utils import last_day_of_month


def form_submit(session_state: SessionStateProxy) -> None:
    """
    Update the session_state values according to selected dates and transport types.
    """
    min_date: date = session_state[StateKeys.SELECTED_MONTH]
    max_date: date = last_day_of_month(min_date)
    date_range = (min_date, max_date)

    selected_tr_types = session_state[StateKeys.SELECTED_TR_TYPES]
    if len(selected_tr_types) == 0:
        st.error(
            body='Lūdzu izvēlies vismaz vienu transporta veidu',
            icon=':material/error:',
        )
        return

    update_available_tr_types(
        db,
        session_state,
        date_range=date_range,
    )
    session_state[StateKeys.METRICS][MetricsKeys.TOTAL_RIDES] = get_total_rides(
        db,
        date_range,
        selected_tr_types,
    )
    session_state[StateKeys.METRICS][MetricsKeys.TOTAL_RIDES_UP_TO_MONTH] = (
        get_total_rides_up_to_month(db, min_date, selected_tr_types)
    )
