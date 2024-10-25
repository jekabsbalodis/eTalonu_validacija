let chartInstance = null;

async function createChart(data_url, chartId) {
    const response = await fetch(data_url);
    const validations = await response.json();

    chartInstance = new Chart(
        document.getElementById(chartId),
        {
            type: 'bar',
            data: validations
        }
    );
    return chartInstance;
};

async function updateCreatedChart(data_url) {
    const response = await fetch(data_url);
    const validations = await response.json();

    chartInstance.data = validations;

    chartInstance.update();
};
