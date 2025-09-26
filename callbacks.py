"""
Callback functions to pass to streamlit widgets.
"""

from datetime import date

from polars import DataFrame
import streamlit as st

from database import db


def _get_available_options(
    date_range: tuple[date, date] | None = None,
    tr_types: list[str] | None = None,
    routes: list[str] | None = None,
) -> tuple[DataFrame, DataFrame]:
    """
    Get available transport types and routes based on current filters.
    """

    rel = db.get_relation("""--sql
                          select TMarsruts, TranspVeids, Laiks as laiks
                          from validacijas;
                          """)

    if date_range and len(date_range) == 2:
        start_date, end_date = date_range
        rel = rel.filter(f"laiks >= '{start_date}' and laiks < '{end_date}'::DATE + 1")

    if tr_types:
        rel = rel.filter(f'TranspVeids IN {tuple(tr_types)}')

    if routes:
        rel = rel.filter(f'TMarsruts IN {tuple(routes)}')

    available_transport_types = (
        rel.select('TranspVeids').unique('TranspVeids').sort('TranspVeids').pl()
    )

    available_routes = (
        rel.select('TMarsruts').unique('TMarsruts').sort('TMarsruts').pl()
    )

    return available_transport_types, available_routes


def update_available_options():
    """
    Update available options based on current selections.
    """
    current_dates = st.session_state.get('selected_dates')
    current_tr_types = st.session_state.get('selected_tr_types')
    current_routes = st.session_state.get('selected_routes')

    available_tr_types, available_routes = _get_available_options(
        date_range=current_dates,
        tr_types=current_tr_types,
        routes=current_routes,
    )

    st.session_state.available_tr_types = available_tr_types.to_series().to_list()
    st.session_state.available_routes = available_routes.to_series().to_list()

    if (
        len(st.session_state.get('selected_tr_types', [])) == 0
        and st.session_state.tr_types == st.session_state.available_tr_types
    ):
        st.session_state.selected_tr_types = st.session_state.available_tr_types


def route_select():
    st.session_state.init_download = True
