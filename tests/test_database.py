from unittest.mock import MagicMock, patch

from streamlit import cache_resource

from database import DatabaseConnection


def test_database_connection_singleton():
    """Test that the DatabaseConnection class is a singleton"""
    DatabaseConnection._instance = None

    db1 = DatabaseConnection(token='test_token')
    db2 = DatabaseConnection(token='test_token')

    assert db1 is db2

    cache_resource.clear()


def test_database_connection_conn_property():
    """Test the conn property of the DatabaseConnection class"""
    DatabaseConnection._instance = None

    with patch('database.duckdb.connect') as mock_connect:
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn
        db = DatabaseConnection(token='test_token')
        con = db.conn
        assert con is mock_conn
        mock_connect.assert_called_once_with(
            'md:validacijas?motherduck_token=test_token', read_only=True
        )

    cache_resource.clear()


def test_get_relation_without_params():
    """Test get_relation without SQL parameters"""
    DatabaseConnection._instance = None

    with patch('database.duckdb.connect'):
        db = DatabaseConnection(token='test_token')
        sql_query = """--sql
                    select 1;
                    """
        db.get_relation(sql_query=sql_query)
        db.conn.sql.assert_called_once_with(query=sql_query)  # type: ignore

    cache_resource.clear()


def test_get_relation_with_params():
    """Test get_relation with SQL parameters"""
    DatabaseConnection._instance = None

    with patch('database.duckdb.connect'):
        db = DatabaseConnection(token='test_token')
        sql_query = """--sql
                    select ?;
                    """
        sql_params = {'1': 1}
        db.get_relation(sql_query=sql_query, sql_params=sql_params)
        db.conn.sql.assert_called_once_with(query=sql_query, params=sql_params)  # type: ignore

    cache_resource.clear()
