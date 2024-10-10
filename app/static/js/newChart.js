function createChart(chartId, labels, datasets) {
    new Chart(
        document.getElementById(chartId),
        {
            type: 'bar',
            data: {
                labels: labels,
                datasets: datasets
            }
        }
    );
}
