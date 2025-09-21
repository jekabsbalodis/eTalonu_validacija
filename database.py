"""
DuckDB in-memory database connection.
"""

import duckdb
import streamlit as st


class DatabaseConnection:
    """
    DuckDB connection wrapper with caching and some utility methods.
    """

    def __init__(self):
        self._conn: duckdb.DuckDBPyConnection | None = None

    @property
    def conn(self) -> duckdb.DuckDBPyConnection:
        """
        Get the cached DuckDB connection.
        """

        if self._conn is None:
            self._conn = self._create_connection()
        return self._conn

    @staticmethod
    @st.cache_resource
    def _create_connection() -> duckdb.DuckDBPyConnection:
        """
        Create cached DuckDB in-memory connection.
        """
        return duckdb.connect()


database = DatabaseConnection()
