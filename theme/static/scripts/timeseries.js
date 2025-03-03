window.usageJourneyVolumeTimeseries = null;

window.chartJSOptions = {
    scales: {
        x: {
            type: 'time',
            time: {
                tooltipFormat: 'yyyy'
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
};

window.avalaibleOptionsTimeGranularity = {
    "month": [{'label':'Monthly','value':'month'}, {'label':'Yearly','value':'year'}],
    "year": [{'label':'Yearly','value':'year'}]
}

function editFrequencyField(){
    let initialUsageJourneyVolumeTimespan = document.querySelector("select" + "[name='initial_usage_journey_volume_timespan']").value;
    let netGrowthRateTimespan = document.querySelector("select" + "[name='net_growth_rate_timespan']");
    netGrowthRateTimespan.innerHTML = '';
    let optionsToFill = window.avalaibleOptionsTimeGranularity[initialUsageJourneyVolumeTimespan];
    optionsToFill.forEach((option) => {
        let optionElement = document.createElement('option');
        optionElement.value = option.value;
        optionElement.textContent = option.label;
        netGrowthRateTimespan.appendChild(optionElement);
    });
}

function sumUsageJourneyVolumeByDisplayGranularity(dailyUsageJourneyVolume, displayGranularity) {
    let aggregatedData = {};
    Object.keys(dailyUsageJourneyVolume).forEach((date, index) => {
        let dateObj = luxon.DateTime.fromISO(date);
        let key;

        if (displayGranularity === "month") {
            key = `${dateObj.year}-${String(dateObj.month).padStart(2, "0")}`;
        } else if (displayGranularity === "year") {
            key = `${dateObj.year}`;
        } else {
            key = date;
        }
        if (!aggregatedData[key]) {
            aggregatedData[key] = 0;
        }
        aggregatedData[key] += dailyUsageJourneyVolume[date];
    });

    return aggregatedData;
}


function updateTimeseriesChart() {
    let displayGranularity = document.getElementById('display_granularity').value;
    let usageJourneyVolume = sumUsageJourneyVolumeByDisplayGranularity(window.dailyUsageJourneyVolume, displayGranularity);

    if (window.chart) {
        window.chart.destroy();
        window.chart = null;
    }

    let displayGranularityToolTipOption = {"month": "MMM yyyy", "year": "yyyy"};

    window.chartJSOptions.scales.x.time.tooltipFormat = displayGranularityToolTipOption[displayGranularity];

    const ctx = document.getElementById("timeSeriesChart").getContext('2d');
        window.chart = new Chart(ctx, {
            type: "line",
            data: {
            labels: Object.keys(usageJourneyVolume),
            datasets: [{
                label: 'User journeys',
                borderColor: '#017E7E',
                backgroundColor: '#017E7E',
                data: Object.values(usageJourneyVolume),
                fill: false,
                tension: 0.5
            }]
        },
            options: window.chartJSOptions
    });

}

function initChart(){
    createTimeSeriesChart()
    updateTimeseriesChart();
}
