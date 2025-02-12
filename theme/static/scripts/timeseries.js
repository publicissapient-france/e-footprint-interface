window.indexInput ={
    'daily': {"value":1, "max":24},
    'weekly': {"value":1, "max":7},
    'seasonal': {"value":1, "max":12}
}

window.charts = {
    'timeSeriesChart' : null,
    'frequencyChart' : null,
    'dailyVariationChart' : null,
    'weeklyVariationChart': null,
    'seasonalVariationChart': null
};

window.timeseriesToSave = [];

const baseDataset = {
    label: 'User journeys',
    borderColor: '#017E7E',
    backgroundColor: '#017E7E'
};

const basePlugins = {
    tooltip: {
        mode: 'index',
        intersect: false
    },
    legend: { display: false }
};

const baseOptions = {
    scales: {
        x: { type: 'category', title: { display: false } },
        y: { display: false, title: { display: false } }
    },
    plugins: basePlugins,
    responsive: true,
    maintainAspectRatio: false
}

window.optionsChartJs={
    'timeSeriesChart' : {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                ...baseDataset,
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
    },
    frequencyChart: {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                ...baseDataset,
                data: [],
                fill: {
                    target: 'start',
                    above: '#a4dcdc',
                    below: '#a4dcdc'
                },
                tension: 0.5
            }]
        },
        options: {
            scales: {
                x: {
                    type: 'category',
                    title: { display: false },
                    grid: { display: false },
                    ticks: {
                        maxTicksLimit: 5,
                        autoSkip: true
                    }
                },
                y: {
                    display: false,
                    title: { display: false },
                    grid: { display: false }
                }
            },
            plugins: basePlugins,
            responsive: true,
            maintainAspectRatio: false
        }
    },
    dailyVariationChart: {
        type: 'bar',
        data: {
            labels: Array.from({ length: 24 }, (_, i) => `${i}`),
            datasets: [{
                ...baseDataset,
                data: Array(24).fill(Math.ceil(getConvertedVolume() / 24)).map(value => value.toFixed(2)),
                fill: true,
                tension: 0
            }]
        },
        options: baseOptions
    },
    weeklyVariationChart: {
        type: 'bar',
        data: {
            labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
            datasets: [{
                ...baseDataset,
                data: Array(7).fill(Math.ceil(getConvertedVolume())).map(value => value.toFixed(2)),
                fill: true,
                tension: 0
            }]
        },
        options: baseOptions
    },
    seasonalVariationChart: {
        type: 'bar',
        data: {
            labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
            datasets: [{
                ...baseDataset,
                data: [],
                fill: true,
                tension: 0
            }]
        },
        options: baseOptions
    }
};

function refreshFormValue(){
    window.formValues = {
        'timeframe_start_date': document.getElementById('timeframe_start_date'),
        'net_growth_rate_range': document.getElementById('net_growth_rate_range'),
        'net_growth_rate_value': document.getElementById('net_growth_rate_value'),
        'avg_nb_usage_journey_value': document.getElementById('avg_nb_usage_journey_value'),
        'avg_nb_usage_journey_range': document.getElementById('avg_nb_usage_journey_range'),
        'timeframe_value': document.getElementById('timeframe_value'),
        'timeframe_range': document.getElementById('timeframe_range')
    }
}

function getConvertedVolume(){
    refreshFormValue();
    let growthRateDuration = luxon.Duration.fromObject({ [window.formValues['net_growth_rate_range'].value]: 1 });
    let avgNbUsageJourneyRange = luxon.Duration.fromObject({ [window.formValues['avg_nb_usage_journey_range'].value]: 1 });
    let startDate = luxon.DateTime.fromISO(window.formValues['timeframe_start_date'].value);
    let ratioDay = (startDate.plus(growthRateDuration).diff(startDate, 'days').days)/avgNbUsageJourneyRange.shiftTo('days').days;
    return window.formValues['avg_nb_usage_journey_value'].value * ratioDay;
}


function initOrUpdateChart(chartName, newData, newOptions) {
  let baseConfig = window.optionsChartJs[chartName];

  if (!window.charts[chartName]) {
    const ctx = document.getElementById(chartName).getContext('2d');
    window.charts[chartName] = new Chart(ctx, {
      type: baseConfig.type,
      data: newData || baseConfig.data,
      options: newOptions || baseConfig.options
    });
  } else {
    let chart = window.charts[chartName];
    if (newData) {
      chart.data.labels = newData.labels;
      chart.data.datasets = newData.datasets;
    }
    if (newOptions) {
      chart.options = {
        ...chart.options,
        ...newOptions
      };
    }
    chart.update();
  }
}

function updateTimeseriesChart() {
    refreshFormValue();
    let periodAnalysis = document.getElementById('timeseries_period_analysis').value;
    let kpiAnalysis = document.getElementById('timeseries_kpi_analysis').value;
    let variationsIndex = window.variationsIndex;
    let variationsValues = window.variationsValues;
    let aggregatedIndex = [];
    let aggregatedValues = [];
    let currentGroup = [];
    let currentDate = luxon.DateTime.fromISO(window.formValues['timeframe_start_date'].value)

    let normalizedIndex = variationsIndex.map(date =>
        luxon.DateTime.fromISO(date).toUTC().toISO()
    );

    function reduceData(){
        if (currentGroup.length > 0) {
            aggregatedIndex.push(currentDate.toISO());
            if (kpiAnalysis === 'sum') {
                aggregatedValues.push(currentGroup.reduce((a, b) => a + b, 0));
            } else if (kpiAnalysis === 'avg') {
                aggregatedValues.push(
                    currentGroup.reduce((a, b) => a + b, 0) / currentGroup.length
                );
            }
            else if (kpiAnalysis === 'cumsum') {
                let lastCumulative = aggregatedValues.length
                    ? aggregatedValues[aggregatedValues.length - 1]
                    : 0;
                aggregatedValues.push(
                    lastCumulative + currentGroup.reduce((a, b) => a + b, 0)
                );
            }
        }
        return aggregatedValues;
    }

    for (let i = 0; i < normalizedIndex.length; i++) {
        let date = luxon.DateTime.fromISO(normalizedIndex[i]);
        let value = variationsValues[i];
        while (date >= currentDate.plus({ [periodAnalysis]: 1 })) {
            reduceData();
            currentDate = currentDate.plus({ [periodAnalysis]: 1 });
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
                label: `User journeys (${kpiAnalysis})`,
                data: aggregatedValues
            }
        ]
    });
    }

function frequencyChart(launchTimeSeriesChart = false){
    refreshFormValue();
    let avgNbUsageJourneyValue  = parseInt(window.formValues['avg_nb_usage_journey_value'].value);
    let avgNbUsageJourneyRange = window.formValues['avg_nb_usage_journey_range'].value;
    let netGrowthRateRange = window.formValues['net_growth_rate_range'].value;
    let timeframeValue= parseInt(window.formValues['timeframe_value'].value);
    let timeframeRange = window.formValues['timeframe_range'].value;

    let dateLooper = luxon.DateTime.local().startOf('year');
    let dateGrowth = luxon.DateTime.local().startOf('year');
    let growthRateFrame = luxon.Duration.fromObject({ [netGrowthRateRange]: 1 });
    let timeframe = luxon.Duration.fromObject({ [timeframeRange]: timeframeValue });
    let periodStep = 0;
    let results = [];
    let labels = [];

    let dailyAvgNbUsageJourneyValue = 0;
    if (avgNbUsageJourneyRange !== 'day') {
        dailyAvgNbUsageJourneyValue = Math.ceil(
            avgNbUsageJourneyValue /
            luxon.Duration.fromObject({ [avgNbUsageJourneyRange]: 1 }).shiftTo('days').days
        );
    } else {
        dailyAvgNbUsageJourneyValue = avgNbUsageJourneyValue;
    }

    results.push(dailyAvgNbUsageJourneyValue.toFixed(2));
    labels.push(dateLooper.toFormat('yyyy-MM-dd'));

    while (periodStep < timeframe.shiftTo(netGrowthRateRange)[`${netGrowthRateRange}s`]-1) {
        dailyAvgNbUsageJourneyValue = Math.ceil(dailyAvgNbUsageJourneyValue * (1 + parseFloat(window.formValues['net_growth_rate_value'].value) / 100));
        dateGrowth = dateGrowth.plus(growthRateFrame);
        dateLooper = dateLooper.plus(growthRateFrame);
        results.push(dailyAvgNbUsageJourneyValue.toFixed(2));
        labels.push(dateLooper.toFormat('yyyy-MM-dd'));
        periodStep++;
    }

    window.optionsChartJs['frequencyChart'].data.labels = labels;
    window.optionsChartJs['frequencyChart'].data.datasets[0].data = results;
    window.optionsChartJs['frequencyChart'].options.scales.x.ticks.maxTicksLimit = timeframeValue;

    initOrUpdateChart('frequencyChart', {
        labels: labels,
        datasets: [
            {
                ...window.optionsChartJs.frequencyChart.data.datasets[0],
                data: results
            }
        ]
    });

    variationChart('daily');
    variationChart('weekly');
    variationChart('seasonal');
    if(launchTimeSeriesChart) {
        createTimeSeriesChart()
        updateTimeseriesChart();
    }
}

function variationChart(periodVariation, launchTimeSeriesChart = false){
    window.adjustedVolumes[periodVariation] = Array(window.indexInput[periodVariation]['max']).fill(1);
    window.variationFactor[periodVariation] = Array(window.indexInput[periodVariation]['max']).fill(1);

    let totalVolume = getConvertedVolume();
    let elementVariations = document.querySelectorAll('[id^="from_' + periodVariation + '_variation_"]');
    elementVariations.forEach(function (element) {
        let idx = element.id.split('_')[element.id.split('_').length - 1];
        let from = parseInt(document.getElementById('from_'+periodVariation+'_variation_' + idx).value);
        let to = parseInt(document.getElementById('to_'+periodVariation+'_variation_' + idx).value);
        let multiplier = parseInt(document.getElementById('multiplier_'+periodVariation+'_variation_' + idx).value);
        if (from !== to) {
            for (let slotTime = from; slotTime < to; slotTime++) {
                window.variationFactor[periodVariation][slotTime] = multiplier;
            }
        }
    });

    let numberOfParts = window.variationFactor[periodVariation].reduce((acc, cur) => acc + cur, 0);
    let partValue = Math.ceil(totalVolume / numberOfParts);

    for(let slotTime=0; slotTime < window.indexInput[periodVariation]['max'] ; slotTime++){
        window.adjustedVolumes[periodVariation][slotTime] = partValue * window.variationFactor[periodVariation][slotTime];
    }

    window.optionsChartJs[periodVariation+'VariationChart'].data.datasets[0].data =
    window.adjustedVolumes[periodVariation].map(value => value.toFixed(2));

    let chartName = periodVariation + 'VariationChart';
    initOrUpdateChart(chartName, {
        labels: window.optionsChartJs[chartName].data.labels,
        datasets: [
        {
        ...window.optionsChartJs[chartName].data.datasets[0],
        data: window.adjustedVolumes[periodVariation].map(value => value.toFixed(2))
        }
        ]
    });
}

function initChart(){
    variationChart('daily');
    variationChart('weekly');
    variationChart('seasonal');
    frequencyChart();
    createTimeSeriesChart()
    updateTimeseriesChart();
}

document.getElementById('usage-pattern-attributes-modal-timeseries').addEventListener('shown.bs.modal', initChart);
