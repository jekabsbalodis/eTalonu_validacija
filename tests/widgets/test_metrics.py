from unittest.mock import MagicMock, Mock, patch

import polars as pl
import pytest

from state_manager import MetricsKeys, StateKeys
from widgets.metrics import render_metrics


@pytest.fixture
def mock_total_rides_df():
    return pl.DataFrame(
        {
            'total_rides': [10000, 12000, 15000],
            'avg_rides_per_day': [333, 400, 500],
            'moy': ['2024-01', '2024-02', '2024-03'],
        }
    )


@pytest.fixture
def mock_rides_per_day_df():
    return pl.DataFrame(
        {
            'total_rides': [450, 480, 520, 490, 510] * 6,
            'dom': [f'2024-03-{i:02d}' for i in range(1, 31)],
        }
    )


@pytest.fixture
def mock_peak_hour_df():
    return pl.DataFrame(
        {
            'avg_rides_per_hour': [
                100,
                150,
                200,
                500,
                600,
                550,
                400,
                300,
                250,
                200,
                180,
                160,
                140,
                130,
                150,
                200,
                350,
                450,
                520,
                480,
                400,
                300,
                250,
                200,
            ],
            'hour': list(range(24)),
        }
    )


@pytest.fixture
def mock_session_state(mock_total_rides_df, mock_rides_per_day_df, mock_peak_hour_df):
    return {
        StateKeys.METRICS: {
            MetricsKeys.TOTAL_RIDES: mock_total_rides_df,
            MetricsKeys.RIDES_PER_DAY: mock_rides_per_day_df,
            MetricsKeys.PEAK_HOUR: mock_peak_hour_df,
        }
    }


@pytest.fixture
def mock_streamlit():
    with patch('widgets.metrics.st') as mock_st:
        mock_col1 = MagicMock()
        mock_col2 = MagicMock()
        mock_col3 = MagicMock()

        mock_st.columns.return_value = [mock_col1, mock_col2, mock_col3]

        mock_col1.__enter__ = Mock(return_value=mock_col1)
        mock_col1.__exit__ = Mock(return_value=False)
        mock_col2.__enter__ = Mock(return_value=mock_col2)
        mock_col2.__exit__ = Mock(return_value=False)
        mock_col3.__enter__ = Mock(return_value=mock_col3)
        mock_col3.__exit__ = Mock(return_value=False)

        mock_st.metric = Mock()

        yield mock_st, mock_col1, mock_col2, mock_col3


class TestRenderMetrics:
    """Tests for render_metrics function."""

    def test_three_columns_are_created(self, mock_streamlit, mock_session_state):
        mock_st, _, _, _ = mock_streamlit

        render_metrics(mock_session_state)

        mock_st.columns.assert_called_once_with(3)

    def test_all_columns_are_used(self, mock_streamlit, mock_session_state):
        _, mock_col1, mock_col2, mock_col3 = mock_streamlit

        render_metrics(mock_session_state)

        mock_col1.__enter__.assert_called_once()
        mock_col2.__enter__.assert_called_once()
        mock_col3.__enter__.assert_called_once()

    @patch('widgets.metrics.format_number')
    @patch('widgets.metrics.format_percent')
    def test_total_rides_metric_rendered(
        self,
        mock_format_percent,
        mock_format_number,
        mock_streamlit,
        mock_session_state,
    ):
        mock_st, _, _, _ = mock_streamlit
        mock_format_number.return_value = '15,000'
        mock_format_percent.return_value = '+25.0%'

        render_metrics(mock_session_state)

        assert mock_st.metric.call_count == 3

        first_call = mock_st.metric.call_args_list[0]
        assert first_call[1]['label'] == 'Braucienu skaits mēnesī'
        assert first_call[1]['value'] == '15,000'
        assert first_call[1]['border'] is True
        assert first_call[1]['chart_type'] == 'area'

    @patch('widgets.metrics.format_number')
    @patch('widgets.metrics.format_percent')
    def test_avg_rides_per_day_metric_rendered(
        self,
        mock_format_percent,
        mock_format_number,
        mock_streamlit,
        mock_session_state,
    ):
        mock_st, _, _, _ = mock_streamlit
        mock_format_number.return_value = '500'
        mock_format_percent.return_value = '+25.0%'

        render_metrics(mock_session_state)

        second_call = mock_st.metric.call_args_list[1]
        assert second_call[1]['label'] == 'Braucienu skaits dienā'
        assert second_call[1]['value'] == '500'
        assert second_call[1]['chart_type'] == 'area'

    @patch('widgets.metrics.format_number')
    @patch('widgets.metrics.format_percent')
    def test_peak_hour_metric_rendered(
        self,
        mock_format_percent,
        mock_format_number,
        mock_streamlit,
        mock_session_state,
    ):
        mock_st, _, _, _ = mock_streamlit
        mock_format_number.return_value = '600'
        mock_format_percent.return_value = '+15.4%'

        render_metrics(mock_session_state)

        third_call = mock_st.metric.call_args_list[2]
        assert 'Aktīvākā stunda: 4.00' in third_call[1]['label']
        assert third_call[1]['value'] == '600'
        assert third_call[1]['chart_type'] == 'bar'
        assert third_call[1]['delta_color'] == 'off'


class TestTotalRidesCalculations:
    """Tests for total rides metric calculations."""

    @patch('widgets.metrics.format_number')
    @patch('widgets.metrics.format_percent')
    def test_total_rides_current_month(
        self,
        mock_format_percent,
        mock_format_number,
        mock_session_state,
    ):
        mock_format_number.return_value = '15,000'
        mock_format_percent.return_value = '+25.0%'

        render_metrics(mock_session_state)

        mock_format_number.assert_any_call(15000)

    @patch('widgets.metrics.format_number')
    @patch('widgets.metrics.format_percent')
    def test_total_rides_delta_calculation(
        self,
        mock_format_percent,
        mock_format_number,
        mock_session_state,
    ):
        mock_format_number.return_value = '15,000'
        mock_format_percent.return_value = '+25.0%'

        render_metrics(mock_session_state)

        expected_delta = (15000 - 12000) / 12000
        mock_format_percent.assert_any_call(expected_delta)

    @patch('widgets.metrics.format_number')
    @patch('widgets.metrics.format_percent')
    def test_total_rides_single_month_handling(
        self,
        mock_format_percent,
        mock_format_number,
        mock_session_state,
    ):
        single_month_df = pl.DataFrame(
            {'total_rides': [10000], 'avg_rides_per_day': [333], 'moy': ['2024-01']}
        )
        mock_session_state[StateKeys.METRICS][MetricsKeys.TOTAL_RIDES] = single_month_df

        mock_format_number.return_value = '10,000'
        mock_format_percent.return_value = '0.0%'

        render_metrics(mock_session_state)

        mock_format_percent.assert_any_call(0.0)

    @patch('widgets.metrics.format_number')
    @patch('widgets.metrics.format_percent')
    def test_total_rides_chart_data(
        self,
        mock_format_percent,
        mock_format_number,
        mock_streamlit,
        mock_session_state,
    ):
        mock_st, _, _, _ = mock_streamlit
        mock_format_number.return_value = '15,000'
        mock_format_percent.return_value = '+25.0%'

        render_metrics(mock_session_state)

        first_call = mock_st.metric.call_args_list[0]
        chart_data = first_call[1]['chart_data']

        assert len(chart_data) == 3
        assert chart_data.to_list() == [10000, 12000, 15000]


class TestAvgRidesPerDayCalculations:
    """Tests for average rides per day calculations."""

    @patch('widgets.metrics.format_number')
    @patch('widgets.metrics.format_percent')
    def test_avg_rides_current_value(
        self,
        mock_format_percent,
        mock_format_number,
        mock_session_state,
    ):
        mock_format_number.return_value = '500'
        mock_format_percent.return_value = '+25.0%'

        render_metrics(mock_session_state)

        mock_format_number.assert_any_call(500)

    @patch('widgets.metrics.format_number')
    @patch('widgets.metrics.format_percent')
    def test_avg_rides_delta_calculation(
        self,
        mock_format_percent,
        mock_format_number,
        mock_session_state,
    ):
        mock_format_number.return_value = '500'
        mock_format_percent.return_value = '+25.0%'

        render_metrics(mock_session_state)

        expected_delta = (500 - 400) / 400
        mock_format_percent.assert_any_call(expected_delta)

    @patch('widgets.metrics.format_number')
    @patch('widgets.metrics.format_percent')
    def test_avg_rides_single_month_handling(
        self,
        mock_format_percent,
        mock_format_number,
        mock_session_state,
    ):
        single_month_df = pl.DataFrame(
            {'total_rides': [10000], 'avg_rides_per_day': [333], 'moy': ['2024-01']}
        )
        mock_session_state[StateKeys.METRICS][MetricsKeys.TOTAL_RIDES] = single_month_df

        mock_format_number.return_value = '333'
        mock_format_percent.return_value = '0.0%'

        render_metrics(mock_session_state)

        mock_format_percent.assert_any_call(0.0)

    @patch('widgets.metrics.format_number')
    @patch('widgets.metrics.format_percent')
    def test_rides_per_day_chart_data(
        self,
        mock_format_percent,
        mock_format_number,
        mock_streamlit,
        mock_session_state,
    ):
        mock_st, _, _, _ = mock_streamlit
        mock_format_number.return_value = '500'
        mock_format_percent.return_value = '+25.0%'

        render_metrics(mock_session_state)

        second_call = mock_st.metric.call_args_list[1]
        chart_data = second_call[1]['chart_data']

        assert len(chart_data) == 30


class TestPeakHourCalculations:
    """Tests for peak hour metric calculations."""

    @patch('widgets.metrics.format_number')
    @patch('widgets.metrics.format_percent')
    def test_peak_hour_identification(
        self,
        mock_format_percent,
        mock_format_number,
        mock_streamlit,
        mock_session_state,
    ):
        mock_st, _, _, _ = mock_streamlit
        mock_format_number.return_value = '600'
        mock_format_percent.return_value = '+15.4%'

        render_metrics(mock_session_state)

        third_call = mock_st.metric.call_args_list[2]
        assert '4.00' in third_call[1]['label']
        mock_format_number.assert_any_call(600)

    @patch('widgets.metrics.format_number')
    @patch('widgets.metrics.format_percent')
    def test_peak_hour_delta_from_median(
        self,
        mock_format_percent,
        mock_format_number,
        mock_session_state,
    ):
        mock_format_number.return_value = '600'
        mock_format_percent.return_value = '+15.4%'

        render_metrics(mock_session_state)

        df = mock_session_state[StateKeys.METRICS][MetricsKeys.PEAK_HOUR]
        median_rides = df.get_column('avg_rides_per_hour').median()
        expected_delta = (600 - median_rides) / median_rides

        mock_format_percent.assert_any_call(expected_delta)

    @patch('widgets.metrics.format_number')
    @patch('widgets.metrics.format_percent')
    def test_peak_hour_chart_data(
        self,
        mock_format_percent,
        mock_format_number,
        mock_streamlit,
        mock_session_state,
    ):
        mock_st, _, _, _ = mock_streamlit
        mock_format_number.return_value = '600'
        mock_format_percent.return_value = '+15.4%'

        render_metrics(mock_session_state)

        third_call = mock_st.metric.call_args_list[2]
        chart_data = third_call[1]['chart_data']

        assert len(chart_data) == 24

    @patch('widgets.metrics.format_number')
    @patch('widgets.metrics.format_percent')
    def test_peak_hour_early_morning(
        self,
        mock_format_percent,
        mock_format_number,
        mock_streamlit,
        mock_session_state,
    ):
        peak_hour_df = pl.DataFrame(
            {
                'avg_rides_per_hour': [100] * 5 + [800] + [200] * 18,
                'hour': list(range(24)),
            }
        )
        mock_session_state[StateKeys.METRICS][MetricsKeys.PEAK_HOUR] = peak_hour_df

        mock_st, _, _, _ = mock_streamlit
        mock_format_number.return_value = '800'
        mock_format_percent.return_value = '+200.0%'

        render_metrics(mock_session_state)

        third_call = mock_st.metric.call_args_list[2]
        assert '5.00' in third_call[1]['label']

    @patch('widgets.metrics.format_number')
    @patch('widgets.metrics.format_percent')
    def test_peak_hour_late_evening(
        self,
        mock_format_percent,
        mock_format_number,
        mock_streamlit,
        mock_session_state,
    ):
        peak_hour_df = pl.DataFrame(
            {'avg_rides_per_hour': [100] * 23 + [750], 'hour': list(range(24))}
        )
        mock_session_state[StateKeys.METRICS][MetricsKeys.PEAK_HOUR] = peak_hour_df

        mock_st, _, _, _ = mock_streamlit
        mock_format_number.return_value = '750'
        mock_format_percent.return_value = '+650.0%'

        render_metrics(mock_session_state)

        third_call = mock_st.metric.call_args_list[2]
        assert '23.00' in third_call[1]['label']

    @patch('widgets.metrics.format_number')
    @patch('widgets.metrics.format_percent')
    def test_peak_hour_zero_median_handling(
        self,
        mock_format_percent,
        mock_format_number,
        mock_streamlit,
        mock_session_state,
    ):
        zero_peak_df = pl.DataFrame(
            {
                'avg_rides_per_hour': [0] * 24,
                'hour': list(range(24)),
            }
        )
        mock_session_state[StateKeys.METRICS][MetricsKeys.PEAK_HOUR] = zero_peak_df

        mock_st, _, _, _ = mock_streamlit
        mock_format_number.return_value = '0'
        mock_format_percent.return_value = '0.0%'

        # Should handle zero median without error
        render_metrics(mock_session_state)

        # Delta should be 0.0 when median is 0 (division by zero handled)
        mock_format_percent.assert_any_call(0.0)


class TestMetricFormatting:
    """Tests for metric formatting and display."""

    @patch('widgets.metrics.format_number')
    @patch('widgets.metrics.format_percent')
    def test_all_metrics_have_borders(
        self,
        mock_format_percent,
        mock_format_number,
        mock_streamlit,
        mock_session_state,
    ):
        mock_st, _, _, _ = mock_streamlit
        mock_format_number.return_value = '1,000'
        mock_format_percent.return_value = '+10.0%'

        render_metrics(mock_session_state)

        for call in mock_st.metric.call_args_list:
            assert call[1]['border'] is True

    @patch('widgets.metrics.format_number')
    @patch('widgets.metrics.format_percent')
    def test_all_metrics_have_help_text(
        self,
        mock_format_percent,
        mock_format_number,
        mock_streamlit,
        mock_session_state,
    ):
        mock_st, _, _, _ = mock_streamlit
        mock_format_number.return_value = '1,000'
        mock_format_percent.return_value = '+10.0%'

        render_metrics(mock_session_state)

        for call in mock_st.metric.call_args_list:
            assert 'help' in call[1]
            assert len(call[1]['help']) > 0

    @patch('widgets.metrics.format_number')
    @patch('widgets.metrics.format_percent')
    def test_all_metrics_stretch_height(
        self,
        mock_format_percent,
        mock_format_number,
        mock_streamlit,
        mock_session_state,
    ):
        mock_st, _, _, _ = mock_streamlit
        mock_format_number.return_value = '1,000'
        mock_format_percent.return_value = '+10.0%'

        render_metrics(mock_session_state)

        for call in mock_st.metric.call_args_list:
            assert call[1]['height'] == 'stretch'

    @patch('widgets.metrics.format_number')
    @patch('widgets.metrics.format_percent')
    def test_peak_hour_delta_color_off(
        self,
        mock_format_percent,
        mock_format_number,
        mock_streamlit,
        mock_session_state,
    ):
        mock_st, _, _, _ = mock_streamlit
        mock_format_number.return_value = '600'
        mock_format_percent.return_value = '+15.4%'

        render_metrics(mock_session_state)

        third_call = mock_st.metric.call_args_list[2]
        assert third_call[1]['delta_color'] == 'off'

        first_call = mock_st.metric.call_args_list[0]
        second_call = mock_st.metric.call_args_list[1]
        assert 'delta_color' not in first_call[1]
        assert 'delta_color' not in second_call[1]


class TestDataFrameInteractions:
    """Tests for DataFrame operations."""

    @patch('widgets.metrics.format_number')
    @patch('widgets.metrics.format_percent')
    def test_correct_dataframes_accessed(
        self,
        mock_format_percent,
        mock_format_number,
        mock_session_state,
    ):
        mock_format_number.return_value = '1,000'
        mock_format_percent.return_value = '+10.0%'

        original_metrics = mock_session_state[StateKeys.METRICS]

        render_metrics(mock_session_state)

        assert StateKeys.METRICS in mock_session_state
        assert MetricsKeys.TOTAL_RIDES in original_metrics
        assert MetricsKeys.RIDES_PER_DAY in original_metrics
        assert MetricsKeys.PEAK_HOUR in original_metrics

    @patch('widgets.metrics.format_number')
    @patch('widgets.metrics.format_percent')
    def test_polars_operations_dont_mutate_original(
        self,
        mock_format_percent,
        mock_format_number,
        mock_session_state,
    ):
        """Test that Polars operations don't mutate original DataFrames."""
        mock_format_number.return_value = '1,000'
        mock_format_percent.return_value = '+10.0%'

        original_total = mock_session_state[StateKeys.METRICS][
            MetricsKeys.TOTAL_RIDES
        ].clone()
        original_peak = mock_session_state[StateKeys.METRICS][
            MetricsKeys.PEAK_HOUR
        ].clone()

        render_metrics(mock_session_state)

        assert original_total.equals(
            mock_session_state[StateKeys.METRICS][MetricsKeys.TOTAL_RIDES]
        )
        assert original_peak.equals(
            mock_session_state[StateKeys.METRICS][MetricsKeys.PEAK_HOUR]
        )


class TestEdgeCases:
    """Tests for edge cases and error handling."""

    @patch('widgets.metrics.format_number')
    @patch('widgets.metrics.format_percent')
    def test_zero_rides_handling(
        self,
        mock_format_percent,
        mock_format_number,
        mock_session_state,
    ):
        zero_df = pl.DataFrame(
            {
                'total_rides': [0, 0],
                'avg_rides_per_day': [0, 0],
                'moy': ['2024-01', '2024-02'],
            }
        )
        mock_session_state[StateKeys.METRICS][MetricsKeys.TOTAL_RIDES] = zero_df

        mock_format_number.return_value = '0'
        mock_format_percent.return_value = '0.0%'

        render_metrics(mock_session_state)

        mock_format_percent.assert_any_call(0.0)

    @patch('widgets.metrics.format_number')
    @patch('widgets.metrics.format_percent')
    def test_small_rides_handling(
        self,
        mock_format_percent,
        mock_format_number,
        mock_session_state,
    ):
        small_df = pl.DataFrame(
            {
                'total_rides': [1, 2],
                'avg_rides_per_day': [1, 2],
                'moy': ['2024-01', '2024-02'],
            }
        )
        mock_session_state[StateKeys.METRICS][MetricsKeys.TOTAL_RIDES] = small_df

        mock_format_number.return_value = '2'
        mock_format_percent.return_value = '+100.0%'

        render_metrics(mock_session_state)

        expected_delta = (2 - 1) / 1
        mock_format_percent.assert_any_call(expected_delta)

    @patch('widgets.metrics.format_number')
    @patch('widgets.metrics.format_percent')
    def test_zero_to_positive_rides(
        self,
        mock_format_percent,
        mock_format_number,
        mock_session_state,
    ):
        zero_to_positive_df = pl.DataFrame(
            {
                'total_rides': [0, 100],
                'avg_rides_per_day': [0, 10],
                'moy': ['2024-01', '2024-02'],
            }
        )
        mock_session_state[StateKeys.METRICS][MetricsKeys.TOTAL_RIDES] = (
            zero_to_positive_df
        )

        mock_format_number.return_value = '100'
        mock_format_percent.return_value = '0.0%'

        render_metrics(mock_session_state)

        mock_format_percent.assert_any_call(0.0)

    @patch('widgets.metrics.format_number')
    @patch('widgets.metrics.format_percent')
    def test_negative_delta_formatting(
        self,
        mock_format_percent,
        mock_format_number,
        mock_session_state,
    ):
        decreasing_df = pl.DataFrame(
            {
                'total_rides': [15000, 12000],
                'avg_rides_per_day': [500, 400],
                'moy': ['2024-01', '2024-02'],
            }
        )
        mock_session_state[StateKeys.METRICS][MetricsKeys.TOTAL_RIDES] = decreasing_df

        mock_format_number.return_value = '12,000'
        mock_format_percent.return_value = '-20.0%'

        render_metrics(mock_session_state)

        expected_delta = (12000 - 15000) / 15000
        mock_format_percent.assert_any_call(expected_delta)

    @patch('widgets.metrics.format_number')
    @patch('widgets.metrics.format_percent')
    def test_very_large_numbers(
        self,
        mock_format_percent,
        mock_format_number,
        mock_session_state,
    ):
        large_df = pl.DataFrame(
            {
                'total_rides': [1_000_000, 2_000_000, 3_000_000],
                'avg_rides_per_day': [33333, 66666, 100000],
                'moy': ['2024-01', '2024-02', '2024-03'],
            }
        )
        mock_session_state[StateKeys.METRICS][MetricsKeys.TOTAL_RIDES] = large_df

        mock_format_number.return_value = '3,000,000'
        mock_format_percent.return_value = '+50.0%'

        render_metrics(mock_session_state)

        mock_format_number.assert_any_call(3_000_000)
