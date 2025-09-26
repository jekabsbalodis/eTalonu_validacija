"""
Streamlit app for eTalonu validation data visualization.

Loads CSV data from data.gov.lv and displays charts.
"""

import datetime

import streamlit as st

from callbacks import route_select, update_available_options
from database import db

if 'date_bounds' not in st.session_state:
    date_bounds_rel = db.get_relation("""--sql
        select
            date(min(laiks)) as min_date,
            date(max(Laiks)) as max_date
        from
            validacijas;
        """)
    st.session_state.date_bounds = date_bounds_rel.fetchone()
min_date, max_date = st.session_state.date_bounds

if 'tr_types' not in st.session_state:
    tr_types_rel = db.get_relation("""--sql
                                   select distinct TranspVeids
                                   from validacijas
                                   order by TranspVeids;
                                   """)
    st.session_state.tr_types = tr_types_rel.pl().to_series().to_list()

if 'selected_dates' not in st.session_state:
    st.session_state.selected_dates = (
        datetime.date(max_date.year, max_date.month, 1),
        max_date,
    )

if (
    'available_tr_types' not in st.session_state
    or 'available_routes' not in st.session_state
):
    update_available_options()


st.title('🚋 eTalonu validācijas')

with st.sidebar:
    with st.form('filters', border=False, enter_to_submit=False):
        st.header('Vizualizāciju filtri')

        selected_dates = st.date_input(
            label='Laika periods',
            help='Izvēlies laika periodu, par kuru atlasīt datus',
            key='selected_dates',
            value=(),
            min_value=min_date,
            max_value=max_date,
        )

        selected_tr_types = st.segmented_control(
            label='Transporta veids',
            help='Izvēlies par kādiem transporta veidiem apskatīt datus',
            key='selected_tr_types',
            options=st.session_state.tr_types,
            default=st.session_state.available_tr_types,
            selection_mode='multi',
            label_visibility='collapsed',
            width='stretch',
        )

        if st.form_submit_button(
            label='Atlasīt datus',
            type='primary',
            width='stretch',
            on_click=update_available_options,
        ):
            st.session_state.init_download = True

    if st.session_state.get('init_download', None):
        st.divider()
        st.subheader('Maršrutu filtri')
        check = st.toggle(
            label='Atlasīt visus',
            key='route_toggle',
            value=True,
        )
        with st.form('route filters', border=False, enter_to_submit=False):
            for tr_type in st.session_state.available_tr_types:
                match tr_type:
                    case 'Autobuss':
                        abbr = 'A'
                    case 'Tramvajs':
                        abbr = 'Tm'
                    case 'Trolejbuss':
                        abbr = 'Tr'
                st.multiselect(
                    label=tr_type,
                    disabled=check,
                    options=filter(
                        lambda w: w.startswith(abbr), st.session_state.available_routes
                    ),
                )
            st.write('vēl būs')
            st.form_submit_button(
                label='Pielāgot maršrutus',
                type='secondary',
                width='stretch',
            )


st.bar_chart()

with st.expander('**Session state:**'):
    st.session_state
