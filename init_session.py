"""
Initialization for st.session_state.
"""

from datetime import date
import streamlit as st
from database import db


def get_date_bounds() -> tuple[date, date]:
    """
    Get min and max date values from database.
    """
    rel = db.get_relation("""--sql
                          select
                              date(min(Laiks)) as min_date,
                              date(max(Laiks)) as max_date
                          from
                              validacijas;
                              """)
    res = rel.fetchone()
    if res is None:
        raise ValueError('Datubāzē netika atrasta kolona "Laiks"')
    return res


def get_transport_types() -> list[str]:
    """
    Get distinct transport types from database.
    """

    rel = db.get_relation("""--sql
                          select
                              distinct TranspVeids
                          from
                              validacijas
                          order by
                              TranspVeids;
                              """)
    return rel.pl().to_series().to_list()


def get_default_date_range(input_date: date) -> tuple[date, date]:
    """
    Get default date range - first day of db's max_date to db's max_date.
    """
    return (
        date(input_date.year, input_date.month, 1),
        input_date,
    )


def init_state() -> None:
    """
    Initializes necessary st.session_state objects.
    """

    # Date bounds
    if 'date_bounds' not in st.session_state:
        st.session_state.date_bounds = get_date_bounds()

    # Transport types
    if 'tr_types' not in st.session_state:
        st.session_state.tr_types = get_transport_types()

    # Default dates
    if 'selected_dates' not in st.session_state:
        max_date = st.session_state.date_bounds[1]
        st.session_state.selected_dates = get_default_date_range(input_date=max_date)
