"""
Streamlit app for eTalonu validation data visualization.

Loads CSV data from data.gov.lv into Polars and displays charts.
"""

import datetime

import polars as pl
import streamlit as st
from numerize.numerize import numerize

from callbacks import on_checkbox_change, on_date_change, on_routes_change
from data_loading import load_and_parse_data
from month_data import available_months

if 'date_bounds' not in st.session_state:
    st.session_state.date_bounds = available_months.date_bounds()
min_date: datetime.date = st.session_state.date_bounds[0]
max_date: datetime.date = st.session_state.date_bounds[1]

# if 'df' not in st.session_state:
#     st.session_state.df = load_and_parse_data([(max_date.year, max_date.month)])
# df: pl.LazyFrame = st.session_state.df

available_routes = (
    df.select(pl.col('TMarsruts'))
    .unique()
    .sort('TMarsruts')
    .collect()['TMarsruts']
    .to_list()
)

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
        on_change=on_date_change,
    )

    selected_routes = st.multiselect(
        label='Maršruts',
        help='Izvēlies par kādiem maršrutiem apskatīt datus',
        key='selected_routes',
        options=available_routes,
        on_change=on_routes_change,
        args=(available_routes,),
    )

    all_routes = st.checkbox(
        label='Izvēlēties visus maršrutus',
        key='routes_cb',
        on_change=on_checkbox_change,
        args=(available_routes,),
    )
st.metric(
    label='Veikto validāciju skaits',
    value=numerize(df.select(pl.len()).collect().item(), 2),
    border=True,
)
st.write('**download test**')
st.write(df.count())
st.write(available_routes)

st.write('**Session state:**')
st.session_state
