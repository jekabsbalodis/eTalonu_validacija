"""
Streamlit app for eTalonu validation data visualization.

Loads CSV data from data.gov.lv and displays charts.
"""

import datetime

import streamlit as st

from callbacks import form_submit, update_available_options
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

TR_TYPES_ABBR: dict[str, str] = {
    'Autobuss': 'A',
    'Tramvajs': 'Tm',
    'Trolejbuss': 'Tr',
}

st.title('🚋 eTalonu validācijas')

with st.sidebar:
    st.header('Vizualizāciju filtri')
    with st.form('filters', border=False, enter_to_submit=False):
        selected_dates = st.date_input(
            label='Laika periods',
            help='Izvēlies laika periodu, par kuru atlasīt datus',
            key='selected_dates',
            min_value=min_date,
            max_value=max_date,
        )

        selected_tr_types = st.segmented_control(
            label='Transporta veids',
            help='Izvēlies par kādiem transporta veidiem apskatīt datus',
            key='selected_tr_types',
            options=st.session_state.tr_types,
            selection_mode='multi',
            label_visibility='collapsed',
            width='stretch',
        )

        if st.form_submit_button(
            label='Atlasīt datus',
            type='primary',
            width='stretch',
            on_click=form_submit,
        ):
            st.session_state.init_download = True
            st.rerun()

    # if st.session_state.get('init_download', False):
    #     st.divider()
    #     st.subheader('Maršrutu filtri')
    #     st.toggle(
    #         label='Atlasīt visus',
    #         key='route_toggle',
    #         value=True,
    #     )
    #     with st.expander(
    #         'Izvēlēties konkrētus maršrutus',
    #         expanded=not st.session_state.route_toggle,
    #     ):
    #         for tr_type in st.session_state.available_tr_types:
    #             abbr = TR_TYPES_ABBR.get(tr_type, '')
    #             routes_container = st.container()
    #             col1, col2 = routes_container.columns(
    #                 (0.7, 0.3),
    #                 vertical_alignment='bottom',
    #             )
    #             routes_cb = col2.checkbox(
    #                 label='visi',
    #                 key=f'routes_{abbr}_cb',
    #             )
    #             selected_routes = col1.multiselect(
    #                 label=tr_type,
    #                 help='Izvēlies par kādiem maršrutiem apskatīt datus',
    #                 key=f'selected_{abbr}_routes',
    #                 options=filter(
    #                     lambda route: route.startswith(abbr),
    #                     st.session_state.available_routes,
    #                 ),
    #                 disabled=st.session_state.route_toggle,
    #             )
    #     st.button(
    #         label='Pielāgot maršrutus',
    #         type='secondary',
    #         width='stretch',
    #     )


st.bar_chart(st.session_state.bar_chart, x='hour', y='count_star()', color='route', stack=False )

with st.expander(
    '**Session state:**',
):
    st.session_state
