from datetime import date
from unittest.mock import MagicMock, patch

import polars as pl
import pytest

from state_manager import (
    MetricsKeys,
    StateKeys,
    init_state,
    update_available_tr_types,
    update_metrics,
)


@pytest.fixture
def setup_mocks():
    """Setup db connection and session state"""
    mock_db = MagicMock()
    mock_session_state = {}

    return mock_db, mock_session_state


@pytest.fixture
def mock_tr_types():
    """Setup for transport types available in database"""
    return pl.DataFrame({'TranspVeids': ['Autobuss', 'Tramvajs', 'Trolejbuss']})


class TestInitState:
    """Test cases for the init_state function"""

    @pytest.fixture
    def mock_available_months(self):
        """Setup for months available in database"""
        return [
            date(2025, 1, 1),
            date(2025, 2, 1),
            date(2025, 3, 1),
            date(2025, 4, 1),
            date(2025, 5, 1),
            date(2025, 6, 1),
            date(2025, 7, 1),
            date(2025, 8, 1),
            date(2025, 9, 1),
            date(2025, 10, 1),
            date(2025, 11, 1),
            date(2025, 12, 1),
        ]

    def test_init_state_sets_available_months(self, setup_mocks, mock_available_months):
        """Test if get_available_months is called"""
        mock_db, mock_session_state = setup_mocks

        with (
            patch('state_manager.get_available_months') as mock_get_months,
            patch('state_manager.get_available_tr_types'),
            patch('state_manager.update_metrics'),
        ):
            mock_get_months.return_value = mock_available_months

            init_state(mock_db, mock_session_state)

            mock_get_months.assert_called_once_with(mock_db)
            assert StateKeys.AVAILABLE_MONTHS in mock_session_state
            assert (
                mock_session_state[StateKeys.AVAILABLE_MONTHS] == mock_available_months
            )

    def test_init_state_sets_default_month_to_latest(
        self, setup_mocks, mock_available_months
    ):
        """
        Test that init_state sets the default month to latest value of available months
        """
        mock_db, mock_session_state = setup_mocks

        with (
            patch('state_manager.get_available_months') as mock_get_months,
            patch('state_manager.get_available_tr_types'),
            patch('state_manager.update_metrics'),
        ):
            mock_get_months.return_value = mock_available_months

            init_state(mock_db, mock_session_state)

            assert StateKeys.SELECTED_MONTH in mock_session_state
            assert mock_session_state[StateKeys.SELECTED_MONTH] == max(
                mock_available_months
            )

    def test_init_state_initializes_tr_types(self, setup_mocks, mock_tr_types):
        """Test that transport types are initialized"""
        mock_db, mock_session_state = setup_mocks

        with (
            patch('state_manager.get_available_months'),
            patch('state_manager.get_available_tr_types') as mock_get_tr_types,
            patch('state_manager.update_metrics'),
        ):
            mock_get_tr_types.return_value = mock_tr_types

            init_state(mock_db, mock_session_state)

            assert StateKeys.AVAILABLE_TR_TYPES in mock_session_state
            assert StateKeys.SELECTED_TR_TYPES in mock_session_state
            assert (
                mock_session_state[StateKeys.AVAILABLE_TR_TYPES]
                == mock_tr_types['TranspVeids'].to_list()
            )
            assert (
                mock_session_state[StateKeys.SELECTED_TR_TYPES]
                == mock_session_state[StateKeys.AVAILABLE_TR_TYPES]
            )

    def test_init_state_initializes_metrics(self, setup_mocks):
        """Test that metrics are initialized"""
        mock_db, mock_session_state = setup_mocks

        with (
            patch('state_manager.get_available_months'),
            patch('state_manager.get_available_tr_types'),
            patch('state_manager.update_metrics') as mock_get_metrics,
        ):
            init_state(mock_db, mock_session_state)

            assert StateKeys.METRICS in mock_session_state
            assert isinstance(mock_session_state[StateKeys.METRICS], dict)
            mock_get_metrics.assert_called_once()

    def test_init_state_skips_initialized_values(self, setup_mocks):
        """
        Test that functions are not called if values are already stored in session state
        """
        mock_db, mock_session_state = setup_mocks
        mock_session_state.update(
            {
                StateKeys.AVAILABLE_MONTHS: [date(2025, 1, 1), date(2025, 2, 1)],
                StateKeys.SELECTED_MONTH: date(2025, 2, 1),
                StateKeys.AVAILABLE_TR_TYPES: ['Autobuss', 'Tramvajs', 'Trolejbuss'],
                StateKeys.SELECTED_TR_TYPES: ['Tramvajs', 'Trolejbuss'],
                StateKeys.METRICS: {},
            }
        )

        with (
            patch('state_manager.get_available_months') as mock_get_months,
            patch('state_manager.get_available_tr_types') as mock_get_tr_types,
            patch('state_manager.update_metrics') as mock_get_metrics,
        ):
            init_state(mock_db, mock_session_state)  # ty:ignore[invalid-argument-type]

            mock_get_months.assert_not_called()
            mock_get_tr_types.assert_not_called()
            mock_get_metrics.assert_not_called()


def test_update_available_tr_types(setup_mocks, mock_tr_types):
    """Test update_available_tr_types updates session state"""
    mock_db, mock_session_state = setup_mocks
    date_range = (date(2025, 11, 1), date(2025, 11, 30))

    with patch('state_manager.get_available_tr_types') as mock_get_tr_types:
        mock_get_tr_types.return_value = mock_tr_types

        update_available_tr_types(mock_db, mock_session_state, date_range)

        mock_get_tr_types.assert_called_once_with(mock_db, date_range=date_range)

        assert StateKeys.AVAILABLE_TR_TYPES in mock_session_state
        assert (
            mock_session_state[StateKeys.AVAILABLE_TR_TYPES]
            == mock_tr_types['TranspVeids'].to_list()
        )


def test_update_metrics(setup_mocks, mock_tr_types):
    """Test update_metrics updates the metrics in session state"""
    mock_db, mock_session_state = setup_mocks
    date_range = (date(2025, 11, 1), date(2025, 11, 30))
    min_date, max_date = date_range
    tr_types = mock_tr_types['TranspVeids'].to_list()
    mock_session_state[StateKeys.METRICS] = {}

    with (
        patch('state_manager.get_total_rides') as mock_total_rides,
        patch('state_manager.get_rides_per_day') as mock_rides_per_day,
        patch('state_manager.get_peak_hour') as mock_peak_hour,
        patch('state_manager.get_popular_routes') as mock_popular_routes,
        patch('state_manager.get_tr_distribution') as mock_tr_distribution,
        patch('state_manager.get_peak_day') as mock_peak_day,
        patch('state_manager.get_route_density') as mock_route_density,
    ):
        update_metrics(mock_db, mock_session_state, date_range, tr_types)

        mock_total_rides.assert_called_once_with(
            _db=mock_db, up_to_date=max_date, tr_types=tr_types
        )
        mock_rides_per_day.assert_called_once_with(
            _db=mock_db, date_range=date_range, tr_types=tr_types
        )
        mock_peak_hour.assert_called_once_with(
            _db=mock_db, date_range=date_range, tr_types=tr_types
        )
        mock_popular_routes.assert_called_once_with(
            _db=mock_db, date_range=date_range, tr_types=tr_types
        )
        mock_tr_distribution.assert_called_once_with(
            _db=mock_db, date_range=date_range, tr_types=tr_types
        )
        mock_peak_day.assert_called_once_with(
            _db=mock_db, date_range=date_range, tr_types=tr_types
        )
        mock_route_density.assert_called_once_with(
            _db=mock_db, date_range=date_range, tr_types=tr_types
        )

        assert MetricsKeys.TOTAL_RIDES in mock_session_state[StateKeys.METRICS]
        assert MetricsKeys.RIDES_PER_DAY in mock_session_state[StateKeys.METRICS]
        assert MetricsKeys.PEAK_HOUR in mock_session_state[StateKeys.METRICS]
        assert MetricsKeys.POPULAR_ROUTES in mock_session_state[StateKeys.METRICS]
        assert MetricsKeys.TR_DISTRIBUTION in mock_session_state[StateKeys.METRICS]
        assert MetricsKeys.PEAK_DAY in mock_session_state[StateKeys.METRICS]
        assert MetricsKeys.ROUTE_DENSITY in mock_session_state[StateKeys.METRICS]
