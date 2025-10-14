import streamlit as st
from polars import DataFrame
from streamlit.runtime.state.session_state_proxy import SessionStateProxy

from state_manager import MetricsKeys, StateKeys

# sql_popular_routes
# count(*) as 'Braucienu skaits',
# TMarsruts as 'Maršruts',


def render_charts(session_state: SessionStateProxy) -> None:
    """
    Render various charts.
    """
    df_popular_routes: DataFrame = session_state[StateKeys.METRICS][
        MetricsKeys.POPULAR_ROUTES
    ]

    st.markdown(
        body='Populārākie maršruti',
        help='15 populārākie maršruti sakāroti pēc braucienu skaita izvēlētajā mēnesī',
    )

    st.bar_chart(
        data=df_popular_routes,
        x='Maršruts',
        y='Braucienu skaits',
        sort=False,
        x_label='Maršruts',
        y_label='Braucienu skaits',
    )
