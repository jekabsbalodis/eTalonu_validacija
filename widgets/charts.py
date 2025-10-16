import altair as alt
import streamlit as st
from polars import DataFrame
from streamlit.runtime.state.session_state_proxy import SessionStateProxy

from state_manager import MetricsKeys, StateKeys

# sql_popular_routes
# count(*) as 'Braucienu skaits',
# TMarsruts as 'Maršruts',

# sql_peak_days
# case dow ... end as 'Nedēļas diena',
# count(*) / count(distinct date(Laiks)) as 'Braucieni vidēji dienā'

# sql_tr_distr
# count(*) as 'Braucienu skaits',
# TranspVeids as 'Transporta veids'

# sql_route_density
# TMarsruts as 'Maršruts',
# round(count(*) / count(distinct GarNr), 0) as 'Vidējais braucienu skaits'


def render_charts(session_state: SessionStateProxy) -> None:
    """
    Render various charts.
    """
    col1, col2 = st.columns(
        spec=[0.7, 0.3],
        border=True,
    )

    with col1:
        df_peak_days: DataFrame = session_state[StateKeys.METRICS][MetricsKeys.PEAK_DAY]

        st.markdown(
            body='Braucieni pa nedēļas dienām',
            help='Vidējais braucienu skaits katru nedēļas dienu',
        )

        peak_days_bar_chart = (
            alt.Chart(data=df_peak_days)
            .mark_bar()
            .encode(
                x=alt.X('Nedēļas diena').sort(
                    df_peak_days.get_column('Nedēļas diena'),
                ),
                y='Braucieni vidēji dienā',
            )
        )

        st.altair_chart(
            altair_chart=peak_days_bar_chart,
        )

    with col2:
        df_tr_dist: DataFrame = session_state[StateKeys.METRICS][
            MetricsKeys.TR_DISTRIBUTION
        ]

        st.markdown(
            body='Braucienu sadalījums',
            help='Braucienu skaita sadalījums pa transporta līdzekļiem',
        )

        tr_distr_pie_chart = (
            alt.Chart(data=df_tr_dist)
            .mark_arc()
            .encode(
                theta='Braucienu skaits',
                color='Transporta veids',
            )
            .configure_legend(
                orient='bottom',
                direction='vertical',
            )
        )

        st.altair_chart(
            altair_chart=tr_distr_pie_chart,
        )

    with st.container(border=True):
        df_popular_routes: DataFrame = session_state[StateKeys.METRICS][
            MetricsKeys.POPULAR_ROUTES
        ]

        st.markdown(
            body='Populārākie maršruti',
            help="""15 populārākie maršruti
            sakāroti pēc braucienu skaita izvēlētajā mēnesī
            """,
        )

        popular_routes_bar_chart = (
            alt.Chart(data=df_popular_routes)
            .mark_bar()
            .encode(
                x=alt.X('Maršruts').sort('-y'),
                y='Braucienu skaits',
            )
        )

        st.altair_chart(
            altair_chart=popular_routes_bar_chart,
        )

    with st.container(border=True):
        df_route_density: DataFrame = session_state[StateKeys.METRICS][
            MetricsKeys.ROUTE_DENSITY
        ]

        st.markdown(
            body='Maršruta noslogojums',
            help="""Vidējais braucienu skaits
            uz vienu transporta līdzekli katrā maršrutā
            """,
        )

        route_density_bar_chart = (
            alt.Chart(data=df_route_density)
            .mark_bar()
            .encode(
                x=alt.X('Maršruts').sort('-y'),
                y='Vidējais braucienu skaits',
            )
        )

        st.altair_chart(
            altair_chart=route_density_bar_chart,
        )
