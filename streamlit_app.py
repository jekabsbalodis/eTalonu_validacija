"""
Streamlit app for eTalonu validation data visualization.

Loads CSV data from data.gov.lv into DuckDB and displays charts.
"""

import calendar
import datetime

import streamlit as st

from database import duckdb_conn
from month_data import available_months

con = duckdb_conn()


st.title('🚋 eTalonu validācijas')

min_month = available_months.min_month()
min_date: datetime.date | None = None
if min_month:
    min_date = datetime.date(min_month[0], min_month[1], 1)

max_month = available_months.max_month()
max_date: datetime.date | None = None
if max_month:
    last_day: int = calendar.monthrange(max_month[0], max_month[1])[1]
    max_date = datetime.date(max_month[0], max_month[1], last_day)

with st.sidebar:
    st.header('Vizualizāciju filtri')

    selected_dates = st.date_input(
        label='Laika periods',
        help='Izvēlies laika periodu, par kuru atlasīt datus',
        value=(),
        min_value=min_date,
        max_value=max_date,
    )
    if 'selected_dates' not in st.session_state:
        st.session_state.selected_dates = selected_dates
    else:
        st.session_state.selected_dates = selected_dates

    route_selection = st.container()
    routes_cb = True
    all_routes = st.checkbox(
        label='Izvēlēties visus maršrutus',
        value=False,
    )
    if all_routes:
        selected_routes = route_selection.multiselect(
            label='Maršruts',
            help='Izvēlies par kādiem maršrutiem apskatīt datus',
            default=['Tm 1', 'Tm 7'],
            options=['Tm 1', 'Tm 7'],
        )
    else:
        selected_routes = route_selection.multiselect(
            label='Maršruts',
            help='Izvēlies par kādiem maršrutiem apskatīt datus',
            options=['Tm 1', 'Tm 7'],
        )

st.write(selected_dates)
st.write(selected_routes)
st.session_state
