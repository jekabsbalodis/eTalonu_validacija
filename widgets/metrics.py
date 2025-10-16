import polars as pl
import streamlit as st
from streamlit.runtime.state.session_state_proxy import SessionStateProxy

from state_manager import MetricsKeys, StateKeys
from utils import format_number, format_percent

# sql_total_rides
# count(*) as total_rides,
# count(*) / count(distinct date(Laiks)) as avg_rides_per_day,
# date_trunc('month', Laiks) as moy

# sql_peak_hour
# count(*) / count(distinct date(Laiks)) as avg_rides_per_hour,
# hour(Laiks) as hour


def render_metrics(session_state: SessionStateProxy) -> None:
    """
    Render key values as metrics.
    """
    col1, col2, col3 = st.columns(3)

    with col1:
        df: pl.DataFrame = session_state[StateKeys.METRICS][MetricsKeys.TOTAL_RIDES]

        total_rides = df.get_column('total_rides')[-1]
        # From DataFrame's column 'total_rides' get the last value of
        # total rides (the selected month)

        total_rides_per_month = df.get_column('total_rides')
        # Get the list of total rides for every month - df's first column

        try:
            total_rides_previous = total_rides_per_month[-2]
        except IndexError:
            total_rides_previous = total_rides
            # Store the penultimate value as previous month's total rides

        delta_total_rides = (total_rides - total_rides_previous) / total_rides_previous

        st.metric(
            label='Braucienu skaits mēnesī',
            help='Kopējais braucienu skaits mēnesī',
            value=format_number(total_rides),
            border=True,
            chart_data=total_rides_per_month,
            chart_type='area',
            delta=format_percent(delta_total_rides),
            height='stretch',
        )

    with col2:
        df: pl.DataFrame = session_state[StateKeys.METRICS][MetricsKeys.TOTAL_RIDES]

        avg_rides = df.get_column('avg_rides_per_day')[-1]

        avg_rides_per_month = df.get_column('avg_rides_per_day')

        try:
            avg_rides_previous = avg_rides_per_month[-2]
        except IndexError:
            avg_rides_previous = avg_rides

        delta_avg_rides = (avg_rides - avg_rides_previous) / avg_rides_previous

        st.metric(
            label='Braucienu skaits dienā',
            help='Vidējais braucienu skaits vienā dienā mēnesī',
            value=format_number(avg_rides),
            border=True,
            chart_data=avg_rides_per_month,
            chart_type='area',
            delta=format_percent(delta_avg_rides),
            height='stretch',
        )

    with col3:
        df: pl.DataFrame = session_state[StateKeys.METRICS][MetricsKeys.PEAK_HOUR]

        rides_per_hour = df.get_column('avg_rides_per_hour')

        peak_hour_and_rides = df.sort(
            'avg_rides_per_hour',
            descending=True,
        ).head(1)
        peak_hour = peak_hour_and_rides.get_column('hour')
        peak_rides = peak_hour_and_rides.get_column('avg_rides_per_hour')

        avg_rides_per_hour = rides_per_hour.median()

        delta_from_avg = (peak_rides.first() - avg_rides_per_hour) / avg_rides_per_hour

        st.metric(
            label=f'Aktīvākā stunda: {peak_hour.first()}.00',
            help="""
            Kopējais braucienu skaits stundā vidēji dienā izvēlētajā mēnesī.\n
            Delta norāda braucienu skaita atšķirību aktīvākajā stundā
            pret mediāno braucienu skaitu stundā.
            """,
            value=format_number(peak_rides.first()),
            border=True,
            chart_data=rides_per_hour,
            chart_type='bar',
            delta=format_percent(delta_from_avg),
            delta_color='off',
            height='stretch',
        )
