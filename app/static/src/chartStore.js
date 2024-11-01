import { Chart, BarController, BarElement, CategoryScale, LinearScale, Colors } from 'chart.js';

Chart.register(BarController, BarElement, CategoryScale, LinearScale, Colors);
let chartInstance = null;

export const chartStore = {
    dataUrl: '',
    loading: true,

    init() { this.loading = true; },
    destroy() { chartInstance.destroy(); },

    setUrl(newUrl) { this.dataUrl = newUrl; },

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

            chartInstance = new Chart(
                document.getElementById(canvasId),
                {
                    type: 'bar',
                    data: validations
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
            chartInstance.update();
        } catch (error) {
            console.error('Neizdevās atsvaidzināt grafiku', error);
        } finally {
            this.loading = false;
        }
    }
};

