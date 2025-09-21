"""
Streamlit app for eTalonu validation data visualization.

Loads CSV data from data.gov.lv into DuckDB and displays charts.
"""

import streamlit as st

from database import duckdb_conn
from month_data import available_months

con = duckdb_conn()

min_date, max_date = available_months.date_bounds() or (None, None)

st.title('🚋 eTalonu validācijas')

with st.sidebar:
    st.header('Vizualizāciju filtri')

    selected_dates = st.date_input(
        label='Laika periods',
        help='Izvēlies laika periodu, par kuru atlasīt datus',
        value=(),
        min_value=min_date,
        max_value=max_date,
    )

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
