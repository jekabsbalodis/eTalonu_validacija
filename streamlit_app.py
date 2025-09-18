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

selected_dates = st.date_input(
    label='Periods',
    help='Izvēlies laika periodu, par kuru atlasīt datus',
    value=(),
    min_value=min_date,
    max_value=max_date,
    width=320,
)


st.write(available_months.url(2025, 6))
