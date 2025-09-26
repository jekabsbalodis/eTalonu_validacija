"""
Callback functions to pass to streamlit widgets.
"""

from datetime import date

from polars import DataFrame
import streamlit as st

from database import db


def _get_available_options(
    date_range: tuple[date, date] | None = None,
    tr_types: list[str] | None = None,
    routes: list[str] | None = None,
) -> tuple[DataFrame, DataFrame]:
    """
    Get available transport types and routes based on current filters.
    """

    rel = db.get_relation("""--sql
                          select TMarsruts, TranspVeids, Laiks as l
                          from validacijas;
                          """)

    if date_range and len(date_range) == 2:
        start_date, end_date = date_range
        rel = rel.filter(f"l >= '{start_date}' and l < '{end_date}'::DATE + 1")

    print(rel.sql_query())

    if tr_types:
        rel = rel.filter(f'TranspVeids IN {tuple(tr_types)}')

    if routes:
        rel = rel.filter(f'TMarsruts IN {tuple(routes)}')

    available_transport_types = (
        rel.select('TranspVeids').unique('TranspVeids').sort('TranspVeids').pl()
    )

    available_routes = (
        rel.select('TMarsruts').unique('TMarsruts').sort('TMarsruts').pl()
    )

    return available_transport_types, available_routes


def update_available_options():
    """
    Update available options based on current selections.
    """
    current_dates = st.session_state.get('selected_dates')
    current_tr_types = st.session_state.get('selected_tr_types')
    current_routes = st.session_state.get('selected_routes')

    available_tr_types, available_routes = _get_available_options(
        date_range=current_dates,
        tr_types=current_tr_types,
        routes=current_routes,
    )

    st.session_state.available_tr_types = available_tr_types.to_series().to_list()
    st.session_state.available_routes = available_routes.to_series().to_list()

    if (
        len(st.session_state.get('selected_tr_types', [])) == 0
        and st.session_state.tr_types == st.session_state.available_tr_types
    ):
        st.session_state.selected_tr_types = st.session_state.available_tr_types


def form_submit():
    update_available_options()

    # rel = db.get_relation("""--sql
    #                                 select
    #                                     *
    #                                 from
    #                                     validacijas;
    #                                 """).filter("Laiks >= '2025-08-01' and Laiks < '2025-08-31'::DATE + 1")

    # bar_chart_rel = rel.select('hour(laiks) as hour, Ier_id').count('Ier_id', 'hour').select('Ier_id')
    # # bar_chart_rel = bar_chart_rel
    current_dates = st.session_state.get('selected_dates')
    bar_chart_rel = db.conn.sql(
        query="""--sql
                select
                    TMarsruts as route,
                    hour(Laiks) as hour,
                    count(*)
                from
                    validacijas
                where
                    Laiks >= ? and Laiks < ?::DATE + 1 and route like 'Tm%'
                group by
                    hour, route
                order by
                    hour, route;
              """,
        params=(current_dates[0], current_dates[1]),
    )
    print(bar_chart_rel.sql_query())
    st.session_state.bar_chart = bar_chart_rel.pl()


def route_select():
    st.session_state.init_download = True
