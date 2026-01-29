from unittest.mock import MagicMock, Mock, patch

import altair as alt
import polars as pl
import pytest

from state_manager import MetricsKeys, StateKeys
from widgets.charts import render_charts


@pytest.fixture
def mock_peak_days_df():
    return pl.DataFrame(
        {
            'Nedēļas diena': [
                'Pirmdiena',
                'Otrdiena',
                'Trešdiena',
                'Ceturtdiena',
                'Piektdiena',
                'Sestdiena',
                'Svētdiena',
            ],
            'Braucieni vidēji dienā': [1000, 1200, 1100, 1150, 1300, 800, 600],
        }
    )


@pytest.fixture
def mock_tr_distribution_df():
    return pl.DataFrame(
        {
            'Braucienu skaits': [5000, 3000, 2000],
            'Transporta veids': ['Autobuss', 'Tramvajs', 'Trolejbuss'],
        }
    )


@pytest.fixture
def mock_popular_routes_df():
    return pl.DataFrame(
        {
            'Braucienu skaits': [
                1500,
                1200,
                1000,
                800,
                700,
                600,
                500,
                450,
                400,
                350,
                300,
                250,
                200,
                150,
                100,
            ],
            'Maršruts': [f'Maršruts {i}' for i in range(1, 16)],
        }
    )


@pytest.fixture
def mock_route_density_df():
    return pl.DataFrame(
        {
            'Vidējais braucienu skaits': [
                120,
                100,
                90,
                80,
                70,
                60,
                50,
                45,
                40,
                35,
                30,
                25,
                20,
                15,
                10,
            ],
            'Maršruts': [f'Maršruts {i}' for i in range(1, 16)],
        }
    )


@pytest.fixture
def mock_session_state(
    mock_peak_days_df,
    mock_tr_distribution_df,
    mock_popular_routes_df,
    mock_route_density_df,
):
    return {
        StateKeys.METRICS: {
            MetricsKeys.PEAK_DAY: mock_peak_days_df,
            MetricsKeys.TR_DISTRIBUTION: mock_tr_distribution_df,
            MetricsKeys.POPULAR_ROUTES: mock_popular_routes_df,
            MetricsKeys.ROUTE_DENSITY: mock_route_density_df,
        }
    }


@pytest.fixture
def mock_streamlit():
    with patch('widgets.charts.st') as mock_st:
        mock_col1 = MagicMock()
        mock_col2 = MagicMock()
        mock_container1 = MagicMock()
        mock_container2 = MagicMock()

        mock_st.columns.return_value = [mock_col1, mock_col2]
        mock_st.container.side_effect = [mock_container1, mock_container2]

        mock_col1.__enter__ = Mock(return_value=mock_col1)
        mock_col1.__exit__ = Mock(return_value=False)
        mock_col2.__enter__ = Mock(return_value=mock_col2)
        mock_col2.__exit__ = Mock(return_value=False)
        mock_container1.__enter__ = Mock(return_value=mock_container1)
        mock_container1.__exit__ = Mock(return_value=False)
        mock_container2.__enter__ = Mock(return_value=mock_container2)
        mock_container2.__exit__ = Mock(return_value=False)

        mock_st.markdown = Mock()
        mock_st.altair_chart = Mock()

        yield mock_st, mock_col1, mock_col2, mock_container1, mock_container2


class TestRenderCharts:
    """Tests for render_charts function."""

    def test_columns_are_created_with_correct_spec(
        self, mock_streamlit, mock_session_state
    ):
        mock_st, _, _, _, _ = mock_streamlit

        render_charts(mock_session_state)

        mock_st.columns.assert_called_once_with(spec=[0.7, 0.3], border=True)

    def test_all_columns_and_containers_are_used(
        self, mock_streamlit, mock_session_state
    ):
        _, mock_col1, mock_col2, mock_container1, mock_container2 = mock_streamlit

        render_charts(mock_session_state)

        mock_col1.__enter__.assert_called_once()
        mock_col2.__enter__.assert_called_once()
        mock_container1.__enter__.assert_called_once()
        mock_container2.__enter__.assert_called_once()

    def test_peak_days_chart_is_rendered(self, mock_streamlit, mock_session_state):
        mock_st, _, _, _, _ = mock_streamlit

        render_charts(mock_session_state)

        assert mock_st.altair_chart.call_count == 4

        first_chart_call = mock_st.altair_chart.call_args_list[0]
        assert isinstance(first_chart_call[1]['altair_chart'], alt.Chart)

    def test_tr_distribution_chart_is_rendered(
        self, mock_streamlit, mock_session_state
    ):
        mock_st, _, _, _, _ = mock_streamlit

        render_charts(mock_session_state)

        second_chart_call = mock_st.altair_chart.call_args_list[1]
        assert isinstance(second_chart_call[1]['altair_chart'], alt.Chart)

    def test_popular_routes_chart_is_rendered(self, mock_streamlit, mock_session_state):
        mock_st, _, _, _, _ = mock_streamlit

        render_charts(mock_session_state)

        third_chart_call = mock_st.altair_chart.call_args_list[2]
        assert isinstance(third_chart_call[1]['altair_chart'], alt.Chart)

    def test_route_density_chart_is_rendered(self, mock_streamlit, mock_session_state):
        mock_st, _, _, _, _ = mock_streamlit

        render_charts(mock_session_state)

        fourth_chart_call = mock_st.altair_chart.call_args_list[3]
        assert isinstance(fourth_chart_call[1]['altair_chart'], alt.Chart)

    def test_all_markdown_titles_are_rendered(self, mock_streamlit, mock_session_state):
        mock_st, _, _, _, _ = mock_streamlit

        render_charts(mock_session_state)

        assert mock_st.markdown.call_count == 4

        titles = [call[1]['body'] for call in mock_st.markdown.call_args_list]
        assert 'Braucieni pa nedēļas dienām' in titles
        assert 'Braucienu sadalījums' in titles
        assert 'Populārākie maršruti' in titles
        assert 'Maršruta noslogojums' in titles

    def test_all_markdown_help_texts_are_present(
        self, mock_streamlit, mock_session_state
    ):
        mock_st, _, _, _, _ = mock_streamlit

        render_charts(mock_session_state)

        for call in mock_st.markdown.call_args_list:
            assert 'help' in call[1]
            assert len(call[1]['help']) > 0


class TestPeakDaysChart:
    """Tests for peak days chart rendering and configuration."""

    def test_peak_days_chart_uses_bar_mark(self, mock_streamlit, mock_session_state):
        mock_st, _, _, _, _ = mock_streamlit

        render_charts(mock_session_state)

        first_chart_call = mock_st.altair_chart.call_args_list[0]
        chart = first_chart_call[1]['altair_chart']

        assert chart.mark == 'bar'

    def test_peak_days_chart_encodings(self, mock_streamlit, mock_session_state):
        mock_st, _, _, _, _ = mock_streamlit

        render_charts(mock_session_state)

        first_chart_call = mock_st.altair_chart.call_args_list[0]
        chart = first_chart_call[1]['altair_chart']

        x_encoding = chart.encoding.x
        assert x_encoding.shorthand == 'Nedēļas diena'

        y_encoding = chart.encoding.y
        assert y_encoding.shorthand == 'Braucieni vidēji dienā'

    def test_peak_days_chart_sorting(self, mock_streamlit, mock_session_state):
        mock_st, _, _, _, _ = mock_streamlit

        render_charts(mock_session_state)

        first_chart_call = mock_st.altair_chart.call_args_list[0]
        chart = first_chart_call[1]['altair_chart']

        x_encoding = chart.encoding.x
        assert hasattr(x_encoding, 'sort')

    def test_peak_days_markdown_help(self, mock_streamlit, mock_session_state):
        mock_st, _, _, _, _ = mock_streamlit

        render_charts(mock_session_state)

        first_markdown_call = mock_st.markdown.call_args_list[0]
        assert (
            'Vidējais braucienu skaits katru nedēļas dienu'
            in first_markdown_call[1]['help']
        )


class TestTrDistributionChart:
    """Tests for transport distribution chart rendering and configuration."""

    def test_tr_distribution_chart_uses_arc_mark(
        self, mock_streamlit, mock_session_state
    ):
        mock_st, _, _, _, _ = mock_streamlit

        render_charts(mock_session_state)

        second_chart_call = mock_st.altair_chart.call_args_list[1]
        chart = second_chart_call[1]['altair_chart']

        assert chart.mark == 'arc'

    def test_tr_distribution_chart_encodings(self, mock_streamlit, mock_session_state):
        mock_st, _, _, _, _ = mock_streamlit

        render_charts(mock_session_state)

        second_chart_call = mock_st.altair_chart.call_args_list[1]
        chart = second_chart_call[1]['altair_chart']

        theta_encoding = chart.encoding.theta
        assert theta_encoding.shorthand == 'Braucienu skaits'

        color_encoding = chart.encoding.color
        assert color_encoding.shorthand == 'Transporta veids'

    def test_tr_distribution_chart_legend_config(
        self, mock_streamlit, mock_session_state
    ):
        mock_st, _, _, _, _ = mock_streamlit

        render_charts(mock_session_state)

        second_chart_call = mock_st.altair_chart.call_args_list[1]
        chart = second_chart_call[1]['altair_chart']

        legend_config = chart.to_dict()['config']['legend']
        assert legend_config['orient'] == 'bottom'
        assert legend_config['direction'] == 'vertical'

    def test_tr_distribution_markdown_help(self, mock_streamlit, mock_session_state):
        mock_st, _, _, _, _ = mock_streamlit

        render_charts(mock_session_state)

        second_markdown_call = mock_st.markdown.call_args_list[1]
        assert (
            'Braucienu skaita sadalījums pa transporta līdzekļiem'
            in second_markdown_call[1]['help']
        )


class TestPopularRoutesChart:
    """Tests for popular routes chart rendering and configuration."""

    def test_popular_routes_chart_uses_bar_mark(
        self, mock_streamlit, mock_session_state
    ):
        mock_st, _, _, _, _ = mock_streamlit

        render_charts(mock_session_state)

        third_chart_call = mock_st.altair_chart.call_args_list[2]
        chart = third_chart_call[1]['altair_chart']

        assert chart.mark == 'bar'

    def test_popular_routes_chart_encodings(self, mock_streamlit, mock_session_state):
        mock_st, _, _, _, _ = mock_streamlit

        render_charts(mock_session_state)

        third_chart_call = mock_st.altair_chart.call_args_list[2]
        chart = third_chart_call[1]['altair_chart']

        x_encoding = chart.encoding.x
        assert x_encoding.shorthand == 'Maršruts'

        y_encoding = chart.encoding.y
        assert y_encoding.shorthand == 'Braucienu skaits'

    def test_popular_routes_chart_sorting(self, mock_streamlit, mock_session_state):
        mock_st, _, _, _, _ = mock_streamlit

        render_charts(mock_session_state)

        third_chart_call = mock_st.altair_chart.call_args_list[2]
        chart = third_chart_call[1]['altair_chart']

        x_encoding = chart.encoding.x
        assert hasattr(x_encoding, 'sort')
        assert chart.to_dict()['encoding']['x']['sort'] == '-y'

    def test_popular_routes_markdown_help(self, mock_streamlit, mock_session_state):
        mock_st, _, _, _, _ = mock_streamlit

        render_charts(mock_session_state)

        third_markdown_call = mock_st.markdown.call_args_list[2]
        assert '15 populārākie maršruti' in third_markdown_call[1]['help']
        assert 'sakāroti pēc braucienu skaita' in third_markdown_call[1]['help']


class TestRouteDensityChart:
    """Tests for route density chart rendering and configuration."""

    def test_route_density_chart_uses_bar_mark(
        self, mock_streamlit, mock_session_state
    ):
        mock_st, _, _, _, _ = mock_streamlit

        render_charts(mock_session_state)

        fourth_chart_call = mock_st.altair_chart.call_args_list[3]
        chart = fourth_chart_call[1]['altair_chart']

        assert chart.mark == 'bar'

    def test_route_density_chart_encodings(self, mock_streamlit, mock_session_state):
        mock_st, _, _, _, _ = mock_streamlit

        render_charts(mock_session_state)

        fourth_chart_call = mock_st.altair_chart.call_args_list[3]
        chart = fourth_chart_call[1]['altair_chart']

        x_encoding = chart.encoding.x
        assert x_encoding.shorthand == 'Maršruts'

        y_encoding = chart.encoding.y
        assert y_encoding.shorthand == 'Vidējais braucienu skaits'

    def test_route_density_chart_sorting(self, mock_streamlit, mock_session_state):
        mock_st, _, _, _, _ = mock_streamlit

        render_charts(mock_session_state)

        fourth_chart_call = mock_st.altair_chart.call_args_list[3]
        chart = fourth_chart_call[1]['altair_chart']

        x_encoding = chart.encoding.x
        assert hasattr(x_encoding, 'sort')
        assert chart.to_dict()['encoding']['x']['sort'] == '-y'

    def test_route_density_markdown_help(self, mock_streamlit, mock_session_state):
        mock_st, _, _, _, _ = mock_streamlit

        render_charts(mock_session_state)

        fourth_markdown_call = mock_st.markdown.call_args_list[3]
        help_text = fourth_markdown_call[1]['help'].strip()
        assert 'Vidējais braucienu skaits uz vienu transporta līdzekli' in help_text


class TestDataFrameInteractions:
    """Tests for DataFrame operations in charts."""

    def test_correct_dataframes_accessed(self, mock_streamlit, mock_session_state):
        mock_st, _, _, _, _ = mock_streamlit

        original_metrics = mock_session_state[StateKeys.METRICS]

        render_charts(mock_session_state)

        assert StateKeys.METRICS in mock_session_state
        assert MetricsKeys.PEAK_DAY in original_metrics
        assert MetricsKeys.TR_DISTRIBUTION in original_metrics
        assert MetricsKeys.POPULAR_ROUTES in original_metrics
        assert MetricsKeys.ROUTE_DENSITY in original_metrics

    def test_polars_operations_dont_mutate_original(self, mock_session_state):
        original_peak_days = mock_session_state[StateKeys.METRICS][
            MetricsKeys.PEAK_DAY
        ].clone()
        original_tr_dist = mock_session_state[StateKeys.METRICS][
            MetricsKeys.TR_DISTRIBUTION
        ].clone()
        original_popular_routes = mock_session_state[StateKeys.METRICS][
            MetricsKeys.POPULAR_ROUTES
        ].clone()
        original_route_density = mock_session_state[StateKeys.METRICS][
            MetricsKeys.ROUTE_DENSITY
        ].clone()

        render_charts(mock_session_state)

        assert original_peak_days.equals(
            mock_session_state[StateKeys.METRICS][MetricsKeys.PEAK_DAY]
        )
        assert original_tr_dist.equals(
            mock_session_state[StateKeys.METRICS][MetricsKeys.TR_DISTRIBUTION]
        )
        assert original_popular_routes.equals(
            mock_session_state[StateKeys.METRICS][MetricsKeys.POPULAR_ROUTES]
        )
        assert original_route_density.equals(
            mock_session_state[StateKeys.METRICS][MetricsKeys.ROUTE_DENSITY]
        )


class TestEdgeCases:
    """Tests for edge cases and error handling."""

    def test_empty_peak_days_dataframe(self, mock_streamlit, mock_session_state):
        empty_df = pl.DataFrame(
            {
                'Nedēļas diena': [],
                'Braucieni vidēji dienā': [],
            }
        )
        mock_session_state[StateKeys.METRICS][MetricsKeys.PEAK_DAY] = empty_df

        render_charts(mock_session_state)

        assert len(mock_streamlit[0].altair_chart.call_args_list) == 4

    def test_single_transport_type(self, mock_streamlit, mock_session_state):
        single_tr_df = pl.DataFrame(
            {
                'Braucienu skaits': [1000],
                'Transporta veids': ['Autobuss'],
            }
        )
        mock_session_state[StateKeys.METRICS][MetricsKeys.TR_DISTRIBUTION] = (
            single_tr_df
        )

        render_charts(mock_session_state)

        assert len(mock_streamlit[0].altair_chart.call_args_list) == 4

    def test_fewer_than_15_routes(self, mock_streamlit, mock_session_state):
        few_routes_df = pl.DataFrame(
            {
                'Braucienu skaits': [500, 400, 300],
                'Maršruts': ['Maršruts 1', 'Maršruts 2', 'Maršruts 3'],
            }
        )
        mock_session_state[StateKeys.METRICS][MetricsKeys.POPULAR_ROUTES] = (
            few_routes_df
        )

        render_charts(mock_session_state)

        assert len(mock_streamlit[0].altair_chart.call_args_list) == 4

    def test_zero_values_in_data(self, mock_streamlit, mock_session_state):
        zero_df = pl.DataFrame(
            {
                'Braucienu skaits': [0, 0, 0],
                'Maršruts': ['Maršruts 1', 'Maršruts 2', 'Maršruts 3'],
            }
        )
        mock_session_state[StateKeys.METRICS][MetricsKeys.POPULAR_ROUTES] = zero_df

        render_charts(mock_session_state)

        assert len(mock_streamlit[0].altair_chart.call_args_list) == 4

    def test_very_large_numbers(self, mock_streamlit, mock_session_state):
        large_df = pl.DataFrame(
            {
                'Braucienu skaits': [1_000_000, 2_000_000, 3_000_000],
                'Maršruts': ['Maršruts 1', 'Maršruts 2', 'Maršruts 3'],
            }
        )
        mock_session_state[StateKeys.METRICS][MetricsKeys.POPULAR_ROUTES] = large_df

        render_charts(mock_session_state)

        assert len(mock_streamlit[0].altair_chart.call_args_list) == 4


class TestChartConfiguration:
    """Tests for chart configuration details."""

    def test_peak_days_chart_in_first_column(self, mock_streamlit, mock_session_state):
        mock_st, mock_col1, mock_col2, _, _ = mock_streamlit

        render_charts(mock_session_state)

        assert mock_col1.__enter__.call_count == 1
        assert mock_col2.__enter__.call_count == 1

        assert len(mock_st.altair_chart.call_args_list) == 4

    def test_tr_distribution_chart_in_second_column(
        self, mock_streamlit, mock_session_state
    ):
        mock_st, mock_col1, mock_col2, _, _ = mock_streamlit

        render_charts(mock_session_state)

        assert mock_col2.__enter__.call_count == 1

    def test_popular_routes_in_first_container(
        self, mock_streamlit, mock_session_state
    ):
        mock_st, _, _, mock_container1, _ = mock_streamlit

        render_charts(mock_session_state)

        assert mock_container1.__enter__.call_count == 1

    def test_route_density_in_second_container(
        self, mock_streamlit, mock_session_state
    ):
        mock_st, _, _, _, mock_container2 = mock_streamlit

        render_charts(mock_session_state)

        assert mock_container2.__enter__.call_count == 1

    def test_all_charts_have_borders(self, mock_streamlit, mock_session_state):
        mock_st, _, _, _, _ = mock_streamlit

        render_charts(mock_session_state)

        mock_st.columns.assert_called_with(spec=[0.7, 0.3], border=True)
        mock_st.container.assert_any_call(border=True)
