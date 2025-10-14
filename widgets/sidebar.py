import streamlit as st
from streamlit.runtime.state import SessionStateProxy

from callbacks import form_submit
from state_manager import StateKeys
from utils import format_month_repr


def render_sidebar(session_state: SessionStateProxy) -> None:
    """
    Render sidebar with selection filters.
    """
    with st.sidebar:
        st.header('Vizualizāciju filtri')
        with st.form('filters', border=False, enter_to_submit=False):
            st.select_slider(
                label='Mēnesis',
                help='Izvēlies mēnesi, par kuru atlasīt datus',
                key=StateKeys.SELECTED_MONTH,
                options=session_state[StateKeys.AVAILABLE_MONTHS],
                format_func=format_month_repr,
            )

            st.segmented_control(
                label='Transporta veids',
                help='Izvēlies par kādiem transporta veidiem apskatīt datus',
                key=StateKeys.SELECTED_TR_TYPES,
                options=session_state[StateKeys.AVAILABLE_TR_TYPES],
                selection_mode='multi',
                label_visibility='collapsed',
                width='stretch',
            )

            st.form_submit_button(
                label='Atlasīt datus',
                type='primary',
                width='stretch',
                on_click=form_submit,
                args=(session_state,),
            )
