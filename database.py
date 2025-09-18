"""
DuckDB in-memory database connection.
"""

import duckdb
import streamlit as st


@st.cache_resource()
def duckdb_conn() -> duckdb.DuckDBPyConnection:
    """
    Create cached DuckDB in-memory connection.
    """
    conn = duckdb.connect()
    return conn
