"""
Streamlit app for eTalonu validation data visualization.

Loads CSV data from data.gov.lv and displays charts.
"""

import streamlit as st

from database import db
from state_manager import init_state
from widgets.charts import render_charts
from widgets.metrics import render_metrics
from widgets.sidebar import render_sidebar

init_state(db, st.session_state)


st.title('🚋 eTalonu validācijas')

render_sidebar(st.session_state)

render_metrics(st.session_state)

render_charts(st.session_state)

with st.expander('**Session state:**'):
    st.session_state  # noqa: B018
