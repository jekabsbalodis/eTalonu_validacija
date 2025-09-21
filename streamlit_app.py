"""
Streamlit app for eTalonu validation data visualization.

Loads CSV data from data.gov.lv into DuckDB and displays charts.
"""

import streamlit as st

from callbacks import on_checkbox_change, on_routes_change
from database import database
from month_data import available_months

available_routes = ['Tm 1', 'Tm 7']

min_date, max_date = available_months.date_bounds() or (None, None)

st.title('🚋 eTalonu validācijas')

with st.sidebar:
    st.header('Vizualizāciju filtri')

    selected_dates = st.date_input(
        label='Laika periods',
        help='Izvēlies laika periodu, par kuru atlasīt datus',
        key='selected_dates',
        value=(),
        min_value=min_date,
        max_value=max_date,
    )

    route_selection = st.container()
    all_routes = st.checkbox(
        label='Izvēlēties visus maršrutus',
        value=False,
        key='routes_cb',
        on_change=on_checkbox_change,
        args=(available_routes,),
    )

    selected_routes = route_selection.multiselect(
        label='Maršruts',
        help='Izvēlies par kādiem maršrutiem apskatīt datus',
        key='selected_routes',
        default=st.session_state.get('selected_routes', []),
        options=available_routes,
        on_change=on_routes_change,
        args=(available_routes,),
    )

st.session_state
