"""
Callback functions to pass to streamlit widgets.
"""

import polars as pl
import streamlit as st

from data_loading import get_months, load_and_parse_data


def on_routes_change(available_routes: list[str]):
    """
    Callback to uncheck 'select all' when routes are manually deselected.

    Args:
        available_routes: List of available route options.
    """
    selected_routes = st.session_state.get('selected_routes', [])

    if len(selected_routes) == len(available_routes):
        st.session_state.routes_cb = True

    elif len(st.session_state.selected_routes) < len(available_routes):
        st.session_state.routes_cb = False


def on_checkbox_change(available_routes: list[str]):
    """
    Callback to select all routes when checkbox is checked.

    Args:
        available_routes: List of available route options.
    """
    if st.session_state.routes_cb:
        st.session_state.selected_routes = available_routes
    else:
        st.session_state.selected_routes = []


def on_date_change():
    """
    Callback to handle date input changes.
    """
    selected_dates = st.session_state.get('selected_dates', [])
    selected_routes = st.session_state.get('selected_routes', [])

    if len(selected_dates) == 2:
        # If user has selected date range

        start_date, end_date = st.session_state.selected_dates
        months = get_months(start_date, end_date)

        if months:
            # Get the data for the months corresponding to selected dates

            df = load_and_parse_data(months)
            st.session_state.df = df

        # Build a list of selected routes
        if st.session_state.routes_cb:
            # If user has selected all routes, show every route from new data

            st.session_state.selected_routes = (
                df.select(pl.col('TMarsruts'))
                .unique()
                .sort('TMarsruts')
                .collect()['TMarsruts']
                .to_list()
            )
        else:
            # If user has selected specific routes, show those routes,
            # that also appear in new data

            available_routes = (
                df.select(pl.col('TMarsruts'))
                .unique()
                .sort('TMarsruts')
                .collect()['TMarsruts']
                .to_list()
            )
            st.session_state.selected_routes = [
                route for route in available_routes if route in selected_routes
            ]
