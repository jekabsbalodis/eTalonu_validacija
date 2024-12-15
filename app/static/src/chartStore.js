import { Chart, BarController, BarElement, CategoryScale, LinearScale, Colors, Legend, Tooltip } from 'chart.js';
import zoomPlugin from 'chartjs-plugin-zoom';

Chart.register(BarController, BarElement, CategoryScale, LinearScale, Colors, Legend, Tooltip, zoomPlugin);
let chartInstance = null;

export const chartStore = {
    dataUrl: '',
    loading: true,

    init() { this.loading = true; },
    destroy() { chartInstance.destroy(); },

    setUrl(baseUrl, startDate, endDate) {
        const encdodedStartDate = encodeURIComponent(startDate);
        const encdodedEndDate = encodeURIComponent(endDate);
        this.dataUrl = `${baseUrl}?start_date=${encdodedStartDate}&end_date=${encdodedEndDate}`;
    },

    async fetchChartData() {
        try {
            const response = await fetch(this.dataUrl);
            if (!response.ok) throw new Error('Kļūdaina atbilde no servera.');
            return await response.json();
        } catch (error) {
            console.error('Neizdevās lejuplādēt grafika datus.', error);
            return null;
        }
    },

    async newChart(canvasId) {
        try {
            const validations = await this.fetchChartData();
            if (!validations) return;

            if (chartInstance) {
                chartInstance.destroy();
            }

            chartInstance = new Chart(
                document.getElementById(canvasId),
                {
                    type: 'bar',
                    data: validations,
                    options: {
                        aspectRatio: (4 / 3),
                        plugins: {
                            zoom: {
                                pan: {
                                    enabled: true,
                                    mode: 'x',
                                    modifierKey: 'ctrl'
                                },
                                zoom: {
                                    wheel: {
                                        enabled: true,
                                        modifierKey: 'ctrl'
                                    },
                                    mode: 'x'
                                }
                            }
                        }
                    }
                }
            );
        } catch (error) {
            console.error('Neizdevās izveidot grafiku', error);
        } finally {
            this.loading = false;
        }
    },

    async updateChart() {
        try {
            const validations = await this.fetchChartData();
            if (!validations || !chartInstance) return;

            chartInstance.data = validations;
            chartInstance.resetZoom();
            chartInstance.update();
        } catch (error) {
            console.error('Neizdevās atsvaidzināt grafiku', error);
        } finally {
            this.loading = false;
        }
    },

    resetChartZoom() {
        if (chartInstance) {
            chartInstance.resetZoom();
        }
    },

    zoomIn() {
        if (chartInstance) {
            chartInstance.zoom({ x: 1.1 });
        }
    },

    zoomOut() {
        if (chartInstance) {
            chartInstance.zoom({ x: 2 - 1 / 0.9 });
        }
    }
};

