window.charts = {
    'timeSeriesChart' : null
};

window.timeseriesToSave = [];

window.baseDataset = {
    label: 'User journeys',
    borderColor: '#017E7E',
    backgroundColor: '#017E7E'
};

window.basePlugins = {
    tooltip: {
        mode: 'index',
        intersect: false
    },
    legend: { display: false }
};

window.baseOptions = {
    scales: {
        x: { type: 'category', title: { display: false } },
        y: { display: false, title: { display: false } }
    },
    plugins: window.basePlugins,
    responsive: true,
    maintainAspectRatio: false
}

window.optionsChartJs={
    'timeSeriesChart' : {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                ...window.baseDataset,
                data: [],
                fill: false,
                tension: 0.5
            }]
        },
        options: {
            scales: {
                x: {
                    type: 'time',
                    time: {
                        tooltipFormat: 'dd MMM yyyy',
                        displayFormats: {
                            day: 'dd MMM yyyy',
                            month: 'MMM yyyy',
                            year: 'yyyy'
                        }
                    },
                    ticks: {
                        autoSkip: true,
                        maxTicksLimit: 10
                    },
                    title: { display: false },
                    grid: { display: false }
                },
                y: {
                    display: true,
                    title: { display: false }
                }
            },
            plugins: {
                tooltip: {
                    mode: 'index',
                    intersect: false,
                },
                legend: { display: false },
                responsive: true,
                maintainAspectRatio: false,
                zoom: {
                    zoom: {
                        drag: {enabled: true,},
                        pinch: {enabled: true},
                        mode: 'x',
                    }
                }
            }
        }
    }
};

function refreshFormValue(){
    window.formValues = {
        'modal_timeframe_start_date': document.getElementById('modal_timeframe_start_date'),
        'modal_net_growth_rate_period': document.getElementById('modal_net_growth_rate_period'),
        'modal_net_growth_rate_value': document.getElementById('modal_net_growth_rate_value'),
        'modal_avg_nb_usage_journey_value': document.getElementById('modal_avg_nb_usage_journey_value'),
        'modal_avg_nb_usage_journey_period': document.getElementById('modal_avg_nb_usage_journey_period'),
        'modal_timeframe_value': document.getElementById('modal_timeframe_value'),
        'modal_timeframe_range': document.getElementById('modal_timeframe_range')
    }
}


function initOrUpdateChart(chartName, newData, newOptions) {
  let baseConfig = window.optionsChartJs[chartName];
  if (window.charts[chartName]) {
    window.charts[chartName].destroy();
    window.charts[chartName] = null;
  }

  const ctx = document.getElementById(chartName).getContext('2d');
  window.charts[chartName] = new Chart(ctx, {
    type: baseConfig.type,
    data: newData || baseConfig.data,
    options: newOptions || baseConfig.options
  });
}

function updateTimeseriesChart() {
    refreshFormValue();
    let displayGranularity = document.getElementById('display_granularity').value;
    let variationsIndex = window.variationsIndex;
    let variationsValues = window.variationsValues;
    let aggregatedIndex = [];
    let aggregatedValues = [];
    let currentGroup = [];
    let currentDate = luxon.DateTime.fromISO(window.formValues['modal_timeframe_start_date'].value)

    let normalizedIndex = variationsIndex.map(date =>
        luxon.DateTime.fromISO(date).toUTC().toISO()
    );

    function reduceData(){
        if (currentGroup.length > 0) {
            aggregatedIndex.push(currentDate.toISO());
            aggregatedValues.push(currentGroup.reduce((a, b) => a + b, 0));
        }
        return aggregatedValues;
    }

    for (let i = 0; i < normalizedIndex.length; i++) {
        let date = luxon.DateTime.fromISO(normalizedIndex[i]);
        let value = variationsValues[i];
        while (date >= currentDate.plus({ [displayGranularity]: 1 })) {
            reduceData();
            currentDate = currentDate.plus({ [displayGranularity]: 1 });
            currentGroup = [];
        }
        currentGroup.push(value);
    }

    aggregatedValues = reduceData();

    initOrUpdateChart('timeSeriesChart', {
    labels: aggregatedIndex,
        datasets: [
            {
                ...window.optionsChartJs.timeSeriesChart.data.datasets[0],
                label: `Usage journeys`,
                data: aggregatedValues
            }
        ]
    });
    }

function initChart(){
    createTimeSeriesChart()
    updateTimeseriesChart();
}
