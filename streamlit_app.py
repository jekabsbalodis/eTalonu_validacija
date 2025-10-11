"""
Streamlit app for eTalonu validation data visualization.

Loads CSV data from data.gov.lv and displays charts.
"""

import locale

import streamlit as st

from callbacks import form_submit
from database import db
from state_manager import MetricsKeys, StateKeys, init_state
from utils import format_number

# locale.setlocale(locale.LC_TIME, 'lv_LV.utf8')
print(locale.getlocale(category=LC_TIME))
init_state(db, st.session_state)


st.title('🚋 eTalonu validācijas')

with st.sidebar:
    st.header('Vizualizāciju filtri')
    with st.form('filters', border=False, enter_to_submit=False):
        selected_month = st.select_slider(
            label='Mēnesis',
            help='Izvēlies mēnesi, par kuru atlasīt datus',
            key=StateKeys.SELECTED_MONTH,
            options=st.session_state[StateKeys.AVAILABLE_MONTHS],
            format_func=lambda x: x.strftime('%B %Y'),
        )

        selected_tr_types = st.segmented_control(
            label='Transporta veids',
            help='Izvēlies par kādiem transporta veidiem apskatīt datus',
            key=StateKeys.SELECTED_TR_TYPES,
            options=st.session_state[StateKeys.AVAILABLE_TR_TYPES],
            selection_mode='multi',
            label_visibility='collapsed',
            width='stretch',
        )

        submit_form = st.form_submit_button(
            label='Atlasīt datus',
            type='primary',
            width='stretch',
            on_click=form_submit,
            args=(st.session_state,),
        )
val = (
    st.session_state[StateKeys.METRICS][MetricsKeys.TOTAL_RIDES]
    .to_series()
    .to_list()[0]
)
val23 = (
    st.session_state[StateKeys.METRICS][MetricsKeys.TOTAL_RIDES_UP_TO_MONTH]
    .to_series()
    .to_list()
)

st.metric(
    label='braucienu skaits',
    value=format_number(
        val,
        fraction_digits=2,
    ),
    border=True,
    chart_data=val23,
    chart_type='area',
)

with st.expander('**Session state:**'):
    st.session_state  # noqa: B018
