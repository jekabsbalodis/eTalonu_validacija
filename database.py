"""
DuckDB MotherDuck database connection.
"""

import threading

import duckdb
import streamlit as st


class DatabaseConnection:
    """
    DuckDB connection wrapper with caching and some utility methods.
    """

    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self: 'DatabaseConnection', token: str):
        """
        Initialize the DatabaseConnection instance.
        """
        if getattr(self, '_initialized', False):
            return

        self._conn: duckdb.DuckDBPyConnection | None = None
        self._token = token
        self._initialized = True

    @property
    def conn(self) -> duckdb.DuckDBPyConnection:
        """
        Get the cached DuckDB connection.
        """

        if self._conn is None:
            self._conn = self._create_connection(self._token)
        return self._conn

    @staticmethod
    @st.cache_resource(show_spinner='Veido savienojumu ar datubāzi...', show_time=True)
    def _create_connection(token: str) -> duckdb.DuckDBPyConnection:
        """
        Create cached DuckDB MotherDuck connection.
        """

        return duckdb.connect(
            f'md:validacijas?motherduck_token={token}',
            read_only=True,
        )

    def get_relation(
        self,
        sql_query: str,
        sql_params: dict | None = None,
    ) -> duckdb.DuckDBPyRelation:
        """
        Execute query and return DuckDBPyrelation.

        Args:
            sql_query: SQL query string
            sql_params: dictionary of additional parameters to pass to SQL query

        Returns:
            A DuckDBPyRelation that can be further modified before returning
            a result
        """
        if sql_params:
            result = self.conn.sql(
                query=sql_query,
                params=sql_params,
            )
        else:
            result = self.conn.sql(query=sql_query)

        return result


db = DatabaseConnection(token=st.secrets.duckdb.md_token)
