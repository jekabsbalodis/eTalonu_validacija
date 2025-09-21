import streamlit as st


def on_routes_change(available_routes: list[str]):
    """
    Callback to uncheck 'select all' when routes are manually deselected.
    """

    if len(st.session_state.selected_routes) < len(available_routes):
        st.session_state.routes_cb = False


def on_checkbox_change(available_routes: list[str]):
    """
    Callback to select all routes when checkbox is checked.
    """
    if st.session_state.routes_cb:
        st.session_state.selected_routes = available_routes
