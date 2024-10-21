function createChart(chartId, validations) {
    new Chart(
        document.getElementById(chartId),
        {
            type: 'bar',
            data: validations
        }
    );
}
