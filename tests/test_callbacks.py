from datetime import date
from unittest.mock import patch

import pytest

from callbacks import form_submit
from state_manager import StateKeys


@pytest.fixture
def session_state():
    return {
        StateKeys.SELECTED_MONTH: date(2025, 10, 1),
        StateKeys.SELECTED_TR_TYPES: [],
    }


def test_form_submit_no_transport_types(session_state):
    """Test form_submit shows a toast message and does not call update functions"""
    with (
        patch('callbacks.st.toast') as mock_toast,
        patch('callbacks.update_available_tr_types') as mock_update_tr,
        patch('callbacks.update_metrics') as mock_update_metrics,
    ):
        form_submit(session_state=session_state)

        mock_toast.assert_called_once()
        assert (
            'Lūdzu izvēlies vismaz vienu transporta veidu'
            in mock_toast.call_args[1]['body']
        )

        mock_update_tr.assert_not_called()
        mock_update_metrics.assert_not_called()


def test_form_submit_valid(session_state):
    """
    Test form_submit is successful when valid date and transport types are selected
    """
    session_state[StateKeys.SELECTED_TR_TYPES] = ['Tramvajs']

    with (
        patch('callbacks.st.toast') as mock_toast,
        patch('callbacks.update_available_tr_types') as mock_update_tr,
        patch('callbacks.update_metrics') as mock_update_metrics,
        patch('callbacks.db') as mock_db,
    ):
        form_submit(session_state=session_state)

        mock_update_tr.assert_called_once()
        args1 = mock_update_tr.call_args.kwargs
        assert args1['db'] == mock_db
        assert args1['session_state'] == session_state
        assert args1['date_range'] == (date(2025, 10, 1), date(2025, 10, 31))

        mock_update_metrics.assert_called_once()
        args2 = mock_update_metrics.call_args.kwargs
        assert args2['db'] == mock_db
        assert args2['session_state'] == session_state
        assert args2['date_range'] == (date(2025, 10, 1), date(2025, 10, 31))
        assert args2['tr_types'] == ['Tramvajs']

        mock_toast.assert_not_called()
