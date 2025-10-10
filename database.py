"""
DuckDB MotherDuck database connection.
"""

import threading

import duckdb
import streamlit as st


def singleton(cls):
    """
    Decorator to create a single instance of a class.
    """
    instances = {}
    lock = threading.Lock()

    def get_instance(*args, **kwargs):
        """
        Get the singleton instance of the class.
        """
        if cls not in instances:
            with lock:
                if cls not in instances:
                    instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return get_instance


@singleton
class DatabaseConnection:
    """
    DuckDB connection wrapper with caching and some utility methods.
    """

    def __init__(self: 'DatabaseConnection', token: str):
        """
        Initialize the DatabaseConnection instance.
        """
        self._conn: duckdb.DuckDBPyConnection | None = None
        self._token = token

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
