from datetime import date
from unittest.mock import MagicMock

import polars as pl
import pytest

from data_manager import (
    _get_data_with_filters,
    get_available_months,
    get_available_tr_types,
)


@pytest.fixture
def mock_db():
    """Mock DatabaseConnection with get_relation method"""
    db = MagicMock()
    db.get_relation.return_value = MagicMock(
        pl=MagicMock(return_value=pl.DataFrame({'test': [1, 2]}))
    )
    return db


@pytest.fixture(autouse=True)
def clear_cache():
    """Clear streamlit cache"""
    get_available_months.clear()
    get_available_tr_types.clear()
    yield


class TestGetDataWithFilters:
    """Test cases for _get_data_with_filters function"""

    def test_no_filters(self, mock_db):
        """Test with no filters (empty where clause)"""
        result = _get_data_with_filters(
            db=mock_db,
            sql_query='select * from table {where_clause}',
        )
        mock_db.get_relation.assert_called_once_with('select * from table ', {})
        assert isinstance(result, pl.DataFrame)

    def test_date_range_filter(self, mock_db):
        """Test date range filtering"""
        date_range = (date(2023, 1, 1), date(2023, 1, 31))
        _get_data_with_filters(
            db=mock_db,
            sql_query='select * from table {where_clause}',
            date_range=date_range,
        )
        mock_db.get_relation.assert_called_once()
        call_args = mock_db.get_relation.call_args
        assert '$start_date' in call_args.args[0]
        assert '$end_date' in call_args.args[0]
        assert call_args.args[1]['start_date'] == date_range[0]
        assert call_args.args[1]['end_date'] == date_range[1]

    def test_tr_types_filter(self, mock_db):
        """Test transport type filtering"""
        tr_types = ['bus', 'tram']
        _get_data_with_filters(
            db=mock_db,
            sql_query='select * from table {where_clause}',
            tr_types=tr_types,
        )
        mock_db.get_relation.assert_called_once()
        call_args = mock_db.get_relation.call_args
        assert '$tr_types' in call_args.args[0]
        assert call_args.args[1]['tr_types'] == tr_types

    def test_combined_filters(self, mock_db):
        """Test combined date and transport type filters"""
        date_range = (date(2023, 1, 1), date(2023, 1, 31))
        tr_types = ['bus', 'tram']
        _get_data_with_filters(
            db=mock_db,
            sql_query='select * from table {where_clause}',
            date_range=date_range,
            tr_types=tr_types,
        )
        mock_db.get_relation.assert_called_once()
        call_args = mock_db.get_relation.call_args
        query: str = call_args.args[0]
        assert 'where' in query.lower()
        assert '$start_date' in query.lower()
        assert '$end_date' in query.lower()
        assert 'and' in query.lower()
        assert call_args.args[1]['start_date'] == date_range[0]
        assert call_args.args[1]['end_date'] == date_range[1]
        assert call_args.args[1]['tr_types'] == tr_types

    def test_up_to_date_filter(self, mock_db):
        """Test up_to_date filter"""
        up_to_date = date(2023, 1, 31)
        _get_data_with_filters(
            db=mock_db,
            sql_query='select * from table {where_clause}',
            up_to_date=up_to_date,
        )
        mock_db.get_relation.assert_called_once()
        call_args = mock_db.get_relation.call_args
        assert '$up_to_date' in call_args.args[0]
        assert call_args.args[1]['up_to_date'] == up_to_date


class TestGetAvailableMonths:
    """Test cases for get_available_months function"""

    def test_get_available_months(self, mock_db):
        """Test basic functionality"""
        months_mock = MagicMock()
        months_mock.fetchone.return_value = (
            date(2024, 1, 1),
            date(2024, 12, 31),
        )
        mock_db.get_relation.return_value = months_mock

        result = get_available_months(mock_db)
        assert len(result) == 12
        assert result[0] == date(2024, 1, 1)
        assert result[-1] == date(2024, 12, 1)
        expected_months = list(range(1, 13))
        actual_months = [d.month for d in result]
        assert actual_months == expected_months

    def test_get_available_months_partial_year(self, mock_db):
        """Test with a partial year range"""
        months_mock = MagicMock()
        months_mock.fetchone.return_value = (
            date(2023, 1, 1),
            date(2023, 3, 31),
        )
        mock_db.get_relation.return_value = months_mock

        result = get_available_months(mock_db)
        assert len(result) == 3
        assert result[0] == date(2023, 1, 1)
        assert result[-1] == date(2023, 3, 1)
        expected_months = list(range(1, 4))
        actual_months = [d.month for d in result]
        assert actual_months == expected_months

    def test_get_available_months_single_month(self, mock_db):
        """Test with single month range"""
        months_mock = MagicMock()
        months_mock.fetchone.return_value = (
            date(2025, 1, 1),
            date(2025, 1, 31),
        )
        mock_db.get_relation.return_value = months_mock

        result = get_available_months(mock_db)
        assert len(result) == 1
        assert result[0] == date(2025, 1, 1)
        assert result[-1] == date(2025, 1, 1)
        expected_months = [1]
        actual_months = [d.month for d in result]
        assert actual_months == expected_months

    def test_get_available_months_cross_year(self, mock_db):
        """Test with range crossing year boundary"""
        months_mock = MagicMock()
        months_mock.fetchone.return_value = (
            date(2025, 12, 1),
            date(2026, 1, 31),
        )
        mock_db.get_relation.return_value = months_mock

        result = get_available_months(mock_db)
        assert len(result) == 2
        assert result[0].year == 2025
        assert result[-1].year == 2026
        expected_months = [12, 1]
        actual_months = [d.month for d in result]
        assert actual_months == expected_months

    def test_get_available_months_empty_result(self, mock_db):
        """Test when database returns no data"""
        months_mock = MagicMock()
        months_mock.fetchone.return_value = None
        mock_db.get_relation.return_value = months_mock

        with pytest.raises(
            ValueError, match='Datubāzē netika atrasta kolonna "Laiks".'
        ):
            get_available_months(mock_db)

    def test_get_available_months_same_start_end(self, mock_db):
        """Test when start and end dates are the same"""
        months_mock = MagicMock()
        months_mock.fetchone.return_value = (
            date(2025, 7, 25),
            date(2025, 7, 25),
        )
        mock_db.get_relation.return_value = months_mock

        result = get_available_months(mock_db)
        assert len(result) == 1
        assert result[0] == date(2025, 7, 1)


class TestGetAvailableTrTypes:
    """Tests for get_available_tr_types function"""

    def test_get_available_tr_types(self, mock_db):
        """Test basic functionality"""
        tr_types_mock = MagicMock()
        tr_types_mock.pl.return_value = pl.DataFrame(
            {'TranspVeids': ['Autobuss', 'Tramvajs', 'Trolejbuss']}
        )
        mock_db.get_relation.return_value = tr_types_mock

        date_range = (date(2025, 1, 1), date(2025, 12, 31))

        result = get_available_tr_types(mock_db, date_range)

        assert len(result) == 3
        assert result['TranspVeids'].to_list() == ['Autobuss', 'Tramvajs', 'Trolejbuss']

    def test_single_tr_type(self, mock_db):
        """Test with single transport type available"""
        tr_types_mock = MagicMock()
        tr_types_mock.pl.return_value = pl.DataFrame({'TranspVeids': ['Autobuss']})
        mock_db.get_relation.return_value = tr_types_mock

        date_range = (date(2025, 3, 1), date(2025, 6, 30))

        result = get_available_tr_types(mock_db, date_range)

        assert len(result) == 1
        assert result['TranspVeids'].to_list() == ['Autobuss']

    def test_empty_result(self, mock_db):
        """Test when no transport types are available"""
        tr_types_mock = MagicMock()
        tr_types_mock.pl.return_value = pl.DataFrame({'TranspVeids': []})
        mock_db.get_relation.return_value = tr_types_mock

        date_range = (date(2024, 11, 1), date(2024, 12, 31))

        result = get_available_tr_types(mock_db, date_range)

        assert len(result) == 0

    def test_date_filtering(self, mock_db):
        """Test that date range is properly applied"""
        tr_types_mock = MagicMock()
        tr_types_mock.pl.return_value = pl.DataFrame(
            {'TranspVeids': ['Autobuss', 'Tramvajs', 'Trolejbuss']}
        )
        mock_db.get_relation.return_value = tr_types_mock

        date_range = (date(2024, 1, 1), date(2024, 6, 30))

        _ = get_available_tr_types(mock_db, date_range)

        mock_db.get_relation.assert_called_once()
        call_args = mock_db.get_relation.call_args
        assert '$start_date' in call_args.args[0]
        assert '$end_date' in call_args.args[0]

    def test_special_characters_in_names(self, mock_db):
        """Test transport types with special characters"""
        tr_types_mock = MagicMock()
        tr_types_mock.pl.return_value = pl.DataFrame(
            {'TranspVeids': ['Autobuss #3', 'Tramvajs-12', 'Trolejbuss/A']}
        )
        mock_db.get_relation.return_value = tr_types_mock

        date_range = (date(2023, 1, 1), date(2023, 1, 31))
        result = get_available_tr_types(mock_db, date_range)

        assert len(result) == 3
        assert 'Autobuss #3' in result['TranspVeids'].to_list()
