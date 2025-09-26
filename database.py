"""
DuckDB MotherDuck database connection.
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
    @st.cache_resource(show_spinner='Veido savienojumu ar datubāzi...', show_time=True)
    def _create_connection() -> duckdb.DuckDBPyConnection:
        """
        Create cached DuckDB MotherDuck connection.
        """

        return duckdb.connect(
            f'md:validacijas?motherduck_token={st.secrets.duckdb.md_token}',
            read_only=True,
        )

    def get_relation(
        self,
        sql_query: str,
    ) -> duckdb.DuckDBPyRelation:
        """
        Execute query and return DuckDBPyrelation.

        Args:
            sql_query: SQL query string

        Returns:
            A DuckDBPyRelation that can be further modified before returning
            a result
        """
        result = self.conn.sql(query=sql_query)

        return result


db = DatabaseConnection()
