window.usageJourneyVolumeTimeseries = null;

window.chartJSOptions = {
    scales: {
        x: {
            type: 'time',
            time: {
                tooltipFormat: 'yyyy',
                unit: 'year'
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

function applyMaxLimitOnModalModelingDurationValue() {
    let inputValue = document.getElementById("modal_modeling_duration_value");
    let currentValue = parseInt(inputValue.value);
    let maxValue = parseInt(inputValue.max);
    let errorElement = document.getElementById('modeling_duration_value_error_message');
    if(currentValue <= 0 || isNaN(currentValue) || !currentValue){
        errorElement.innerHTML = "Modeling duration value must be greater than 0 and can't be empty";
        errorElement.style.display = "block";
    }else if (currentValue > maxValue) {
        errorElement.innerHTML = `Modeling duration value must be less than or equal to ${maxValue}`;
        errorElement.style.display = "block";
    }else{
        errorElement.innerHTML ='';
        errorElement.style.display = "none";
        document.getElementById('modeling_duration_value').value = currentValue;
        updateUsageJourneyVolumeTimeseries();
        createOrUpdateTimeSeriesChart();
    }
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

function computeUsageJourneyVolume(
    startDate, modelingDurationValue, modelingDurationUnit, netGrowRateInPercentage, netGrowthRateTimespan,
    initialUsageJourneyVolume, initialUsageJourneyVolumeTimespan) {
    let dailyUsageJourneyVolume = {};

    let luxonStartDate = luxon.DateTime.fromISO(startDate);
    let luxonModelingDuration = luxon.Duration.fromObject({ [modelingDurationUnit]: modelingDurationValue });
    let luxonNetGrowthRateTimespan = luxon.Duration.fromObject({ [netGrowthRateTimespan]: 1 });
    let luxonInitialUsageJourneyVolumeTimespan = luxon.Duration.fromObject({ [initialUsageJourneyVolumeTimespan]: 1 });

    let modelingDurationInDays = luxonModelingDuration.shiftTo('days')['days'];
    let growthRateTimespanInDays = luxonNetGrowthRateTimespan.shiftTo('days')['days'];
    let initialUsageJourneyVolumeTimespanInDays = luxonInitialUsageJourneyVolumeTimespan.shiftTo('days')['days'];

    let dailyGrowthRate = (1 + netGrowRateInPercentage/100) ** (1/growthRateTimespanInDays);
    let firstDailyUsageJourneyVolume = initialUsageJourneyVolume / initialUsageJourneyVolumeTimespanInDays;

    let dateLooper = luxonStartDate;
    let dailyUsageJourneyVolumeLooper = firstDailyUsageJourneyVolume;
    for(let day_nb = 0; day_nb < modelingDurationInDays; day_nb++){
        dailyUsageJourneyVolume[dateLooper.toISO()] = dailyUsageJourneyVolumeLooper;
        dailyUsageJourneyVolumeLooper *= dailyGrowthRate;
        dateLooper = luxonStartDate.plus({ ["day"]: (day_nb+1)});
    }
    return dailyUsageJourneyVolume;
}

function updateUsageJourneyVolumeTimeseries(){
    let startDate = document.getElementById('start_date').value;
    let modelingDurationValue = parseInt(document.getElementById('modeling_duration_value').value);
    let modelingDurationUnit = document.getElementById('modeling_duration_unit').value;
    let netGrowRateInPercentage = parseInt(document.getElementById('net_growth_rate_in_percentage').value);
    let netGrowthRateTimespan = document.getElementById('net_growth_rate_timespan').value;
    let initialUsageJourneyVolume = parseInt(document.getElementById('initial_usage_journey_volume').value);
    let initialUsageJourneyVolumeTimespan = document.getElementById('initial_usage_journey_volume_timespan').value;

    window.dailyUsageJourneyVolume = computeUsageJourneyVolume(
        startDate, modelingDurationValue, modelingDurationUnit, netGrowRateInPercentage, netGrowthRateTimespan,
        initialUsageJourneyVolume, initialUsageJourneyVolumeTimespan);
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

function createOrUpdateTimeSeriesChart(){
    let displayGranularity = document.getElementById('display_granularity').value;
    let usageJourneyVolume = sumUsageJourneyVolumeByDisplayGranularity(
        window.dailyUsageJourneyVolume, displayGranularity);

    if (window.chart) {
        window.chart.destroy();
        window.chart = null;
    }

    let displayGranularityToolTipOption = {"month": "MMM yyyy", "year": "yyyy"};

    window.chartJSOptions.scales.x.time.unit = displayGranularity === "month" ? "month" : "year";
    window.chartJSOptions.scales.x.time.tooltipFormat = displayGranularity === "month" ? "MMM yyyy" : "yyyy";

    const ctx = document.getElementById("timeSeriesChart").getContext('2d');
        window.chart = new Chart(ctx, {
            type: "bar",
            data: {
            labels: Object.keys(usageJourneyVolume),
            datasets: [{
                label: 'Usage journeys',
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

if (typeof module !== "undefined" && module.exports) {
    module.exports = {
        computeUsageJourneyVolume,
        sumUsageJourneyVolumeByDisplayGranularity
    };
}
