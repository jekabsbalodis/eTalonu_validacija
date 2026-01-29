from datetime import date
from unittest.mock import MagicMock, Mock, patch

import pytest

from state_manager import StateKeys
from widgets.sidebar import render_sidebar


@pytest.fixture
def mock_session_state():
    return {
        StateKeys.AVAILABLE_MONTHS: [
            date(2025, 1, 1),
            date(2025, 2, 1),
            date(2025, 3, 1),
        ],
        StateKeys.AVAILABLE_TR_TYPES: ['Autobuss', 'Tramvajs', 'Trolejbuss'],
        StateKeys.SELECTED_MONTH: date(2025, 2, 1),
        StateKeys.SELECTED_TR_TYPES: ['Autobuss', 'Tramvajs'],
    }


@pytest.fixture
def mock_streamlit():
    with patch('widgets.sidebar.st') as mock_st:
        mock_sidebar_context = MagicMock()
        mock_st.sidebar.return_value.__enter__.return_value = mock_sidebar_context

        mock_form_context = MagicMock()
        mock_sidebar_context.form.return_value.__enter__.return_value = (
            mock_form_context
        )

        mock_sidebar_context.header = Mock()
        mock_sidebar_context.divider = Mock()
        mock_sidebar_context.caption = Mock()

        yield mock_st, mock_sidebar_context, mock_form_context


class TestRenderSidebar:
    """Tests for render_sidebar function"""

    def test_sidebar_context_is_used(self, mock_streamlit, mock_session_state):
        mock_st, mock_sidebar, _ = mock_streamlit

        render_sidebar(mock_session_state)

        mock_st.sidebar.__enter__.assert_called_once()
        mock_st.sidebar.__exit__.assert_called_once()

    def test_header_is_rendered(self, mock_streamlit, mock_session_state):
        mock_st, _, _ = mock_streamlit

        render_sidebar(mock_session_state)

        mock_st.header.assert_called_once_with('Vizualizāciju filtri')

    def test_form_is_created_with_correct_params(
        self, mock_streamlit, mock_session_state
    ):
        mock_st, _, _ = mock_streamlit

        render_sidebar(mock_session_state)

        mock_st.form.assert_called_once_with(
            'filters', border=False, enter_to_submit=False
        )

    @patch('widgets.sidebar.format_month_repr')
    def test_month_selector_is_rendered(
        self, mock_format_month_repr, mock_streamlit, mock_session_state
    ):
        mock_st, _, mock_form = mock_streamlit
        mock_form.return_value = '2024. gada februāris'

        render_sidebar(mock_session_state)

        mock_st.select_slider.assert_called_once_with(
            label='Mēnesis',
            help='Izvēlies mēnesi, par kuru atlasīt datus',
            key=StateKeys.SELECTED_MONTH,
            options=mock_session_state[StateKeys.AVAILABLE_MONTHS],
            format_func=mock_format_month_repr,
        )

    def test_transport_type_selector_is_rendered(
        self, mock_streamlit, mock_session_state
    ):
        mock_st, _, _ = mock_streamlit

        render_sidebar(mock_session_state)

        mock_st.segmented_control.assert_called_once_with(
            label='Transporta veids',
            help='Izvēlies par kādiem transporta veidiem apskatīt datus',
            key=StateKeys.SELECTED_TR_TYPES,
            options=mock_session_state[StateKeys.AVAILABLE_TR_TYPES],
            selection_mode='multi',
            label_visibility='collapsed',
            width='stretch',
        )

    @patch('widgets.sidebar.form_submit')
    def test_submit_button_is_rendered(
        self, mock_form_submit, mock_streamlit, mock_session_state
    ):
        mock_st, _, _ = mock_streamlit

        render_sidebar(mock_session_state)

        mock_st.form_submit_button.assert_called_once_with(
            label='Atlasīt datus',
            type='primary',
            width='stretch',
            on_click=mock_form_submit,
            args=(mock_session_state,),
        )

    def test_divider_is_rendered(self, mock_streamlit, mock_session_state):
        mock_st, _, _ = mock_streamlit

        render_sidebar(mock_session_state)

        mock_st.divider.assert_called_once()

    def test_caption_with_links_is_rendered(self, mock_streamlit, mock_session_state):
        mock_st, _, _ = mock_streamlit

        render_sidebar(mock_session_state)

        expected_caption = """
            [Dati no Rīgas Satiksmes](https://data.gov.lv/dati/lv/dataset/e-talonu-validaciju-dati-rigas-satiksme-sabiedriskajos-transportlidzeklos)
            | [Pirmkods](https://codeberg.org/clear9550/eTalonu_validacija)
            """

        mock_st.caption.assert_called_once_with(body=expected_caption)

    def test_render_order_is_correct(self, mock_streamlit, mock_session_state):
        mock_st, _, _ = mock_streamlit

        render_sidebar(mock_session_state)

        all_calls = mock_st.method_calls

        header_index = next(i for i, c in enumerate(all_calls) if c[0] == 'header')
        form_index = next(i for i, c in enumerate(all_calls) if c[0] == 'form')
        divider_index = next(i for i, c in enumerate(all_calls) if c[0] == 'divider')
        caption_index = next(i for i, c in enumerate(all_calls) if c[0] == 'caption')

        assert header_index < form_index
        assert form_index < divider_index
        assert divider_index < caption_index

    def test_empty_available_months_list(self, mock_streamlit, mock_session_state):
        mock_st, _, _ = mock_streamlit

        mock_session_state[StateKeys.AVAILABLE_MONTHS] = []
        mock_session_state[StateKeys.SELECTED_MONTH] = None

        render_sidebar(mock_session_state)

        call_args = mock_st.select_slider.call_args
        assert call_args[1]['options'] == []

    def test_empty_transport_types_list(self, mock_streamlit, mock_session_state):
        mock_st, _, _ = mock_streamlit

        mock_session_state[StateKeys.AVAILABLE_TR_TYPES] = []
        mock_session_state[StateKeys.SELECTED_TR_TYPES] = []

        render_sidebar(mock_session_state)

        call_args = mock_st.segmented_control.call_args
        assert call_args[1]['options'] == []

    def test_single_month_available(self, mock_streamlit, mock_session_state):
        mock_st, _, _ = mock_streamlit

        single_month = date(2023, 12, 1)

        mock_session_state[StateKeys.AVAILABLE_MONTHS] = [single_month]
        mock_session_state[StateKeys.SELECTED_MONTH] = single_month

        render_sidebar(mock_session_state)

        call_args = mock_st.select_slider.call_args
        assert call_args[1]['options'] == [single_month]

    def test_single_transport_type_available(self, mock_streamlit, mock_session_state):
        mock_st, _, _ = mock_streamlit

        single_tr_type = 'Tramvajs'

        mock_session_state[StateKeys.AVAILABLE_TR_TYPES] = [single_tr_type]
        mock_session_state[StateKeys.SELECTED_TR_TYPES] = single_tr_type

        render_sidebar(mock_session_state)

        call_args = mock_st.segmented_control.call_args
        assert call_args[1]['options'] == [single_tr_type]

    @patch('widgets.sidebar.form_submit')
    def test_callback_receives_session_state(
        self, mock_form_submit, mock_streamlit, mock_session_state
    ):
        mock_st, _, _ = mock_streamlit

        render_sidebar(mock_session_state)

        call_args = mock_st.form_submit_button.call_args
        assert call_args[1]['args'] == (mock_session_state,)
        assert call_args[1]['on_click'] == mock_form_submit


class TestSidebarIntegration:
    """Integration tests for sidebar with realistic scenarios"""

    @patch('widgets.sidebar.format_month_repr')
    def test_complete_sidebar_rendering_flow(
        self,
        mock_format_month_repr,
        mock_streamlit,
        mock_session_state,
    ):
        mock_st, _, mock_form = mock_streamlit
        mock_format_month_repr.return_value = '2024. gada februāris'

        render_sidebar(mock_session_state)

        assert mock_st.header.called
        assert mock_st.form.called
        assert mock_st.select_slider.called
        assert mock_st.segmented_control.called
        assert mock_st.form_submit_button.called
        assert mock_st.divider.called
        assert mock_st.caption.called

    def test_sidebar_with_many_months(self, mock_streamlit, mock_session_state):
        mock_st, _, _ = mock_streamlit
        months = [date(2021 + y, m, 1) for y in range(5) for m in range(1, 13)]

        mock_session_state[StateKeys.AVAILABLE_MONTHS] = months
        mock_session_state[StateKeys.SELECTED_MONTH] = months[-1]

        render_sidebar(mock_session_state)

        call_args = mock_st.select_slider.call_args

        assert len(call_args[1]['options']) == 60


class TestSidebarStateKeys:
    """Test that correct StateKeys are used throughout"""

    def test_correct_state_keys_accessed(self, mock_streamlit, mock_session_state):
        mock_st, _, _ = mock_streamlit

        render_sidebar(mock_session_state)

        select_slider_call = mock_st.select_slider.call_args
        assert select_slider_call[1]['key'] == StateKeys.SELECTED_MONTH
        assert (
            select_slider_call[1]['options']
            == mock_session_state[StateKeys.AVAILABLE_MONTHS]
        )

        segmented_control_call = mock_st.segmented_control.call_args
        assert segmented_control_call[1]['key'] == StateKeys.SELECTED_TR_TYPES
        assert (
            segmented_control_call[1]['options']
            == mock_session_state[StateKeys.AVAILABLE_TR_TYPES]
        )
