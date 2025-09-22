"""
Callback functions to pass to streamlit widgets.
"""

import streamlit as st
from data_loading import get_months, load_data
from month_data import available_months
from database import database


def on_routes_change(available_routes: list[str]):
    """
    Callback to uncheck 'select all' when routes are manually deselected.

    Args:
        available_routes: List of available route options.
    """

    if len(st.session_state.selected_routes) < len(available_routes):
        st.session_state.routes_cb = False


def on_checkbox_change(available_routes: list[str]):
    """
    Callback to select all routes when checkbox is checked.

    Args:
        available_routes: List of available route options.
    """
    if st.session_state.routes_cb:
        st.session_state.selected_routes = available_routes
def on_date_change():
    """
    Callback to handle date input changes.
    """
    if not st.session_state.selected_dates:
        return

    if len(st.session_state.selected_dates) == 2:
        start_date, end_date = st.session_state.selected_dates
        months = get_months(start_date, end_date)
        if len(months) == 1:
            print(months[0])
            url = available_months.url(months[0][0], months[0][1])
            print(url)
            for key, value in load_data(url).items():
                print(key)
                database.conn.execute('''--sql
                select * from read_csv_auto(?)
                ''', (key,))
