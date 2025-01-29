let indexInput ={
    'daily': {"value":1, "max":24},
    'weekly': {"value":1, "max":7},
    'seasonal': {"value":1, "max":12}
}

let charts = {
    'timeSeriesChart' : null,
    'frequencyChart' : null,
    'dailyVariationChart' : null,
    'weeklyVariationChart': null,
    'seasonalVariationChart': null
};

let timeseriesToSave = [];

let optionsChartJs={
    'timeSeriesChart' : {
        type: 'line',
        data : {
            labels: [],
            datasets: [{
                label: 'User journeys',
                data: [],
                borderColor: '#017E7E',
                backgroundColor: '#017E7E',
                fill: false,
                tension: 0.5
            }]
        },
        options : {
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
                        maxTicksLimit: 10,
                    },
                    title: {
                        display: false,
                    },
                    grid: {
                        display: false,
                    }
                },
                y: {
                    display: true,
                    title: {
                        display: false,
                    },
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
                        drag: {
                            enabled: true,
                        },
                        pinch: {
                            enabled: true
                        },
                        mode: 'x',
                    }
                }
            }
        }
    },
    'frequencyChart' : {
        type: 'line',
        data : {
            labels: [],
            datasets: [{
                label: 'User journeys',
                data: [],
                borderColor: '#017E7E',
                backgroundColor: '#017E7E',
                fill: {
                    target: 'start',
                    above: '#a4dcdc',
                    below: '#a4dcdc',
                },
                tension: 0.5
            }]
        },
        options : {
            scales: {
                x: {
                    type: 'category',
                    title: {
                        display: false,
                    },
                    grid: {
                        display: false
                    },
                    ticks: {
                        maxTicksLimit: 5,
                        autoSkip: true
                    }
                },
                y: {
                    display: false,
                    title: {
                        display: false,
                    },
                    grid: {
                        display: false
                    }
                }
            },
            plugins: {
                tooltip: {
                    mode: 'index',
                    intersect: false,
                },
                legend: { display: false },
                responsive: false,
                maintainAspectRatio: false
            }
        }
    },
    'dailyVariationChart': {
        type: 'bar',
        data : {
            labels: Array.from({ length: 24 }, (_, i) => `${i}`),
            datasets: [{
                label: 'User journeys',
                data: Array(24).fill(Math.ceil(getTotalVolume('daily')/24)).map(value => value.toFixed(2)),
                borderColor: '#017E7E',
                backgroundColor: '#017E7E',
                fill: true,
                tension: 0
            }]
        },
        options : {
            scales: {
                x: {
                    type: 'category',
                    title: {
                        display: false,
                    }
                },
                y: {
                    display: false,
                    title: {
                        display: false,
                    }
                }
            },
            plugins: {
                tooltip: {
                    mode: 'index',
                    intersect: false,
                },
                legend: { display: false },
                responsive: false,
                maintainAspectRatio: false
            }
        }
    },
    'weeklyVariationChart': {
        type: 'bar',
        data : {
            labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
            datasets: [{
                label: 'User journeys',
                data: Array(7).fill(Math.ceil(getTotalVolume('daily'))).map(value => value.toFixed(2)),
                borderColor: '#017E7E',
                backgroundColor: '#017E7E',
                fill: true,
                tension: 0
            }]
        },
        options : {
            scales: {
                x: {
                    type: 'category',
                    title: {
                        display: false,
                    }
                },
                y: {
                    display: false,
                    title: {
                        display: false,
                    }
                }
            },
            plugins: {
                tooltip: {
                    mode: 'index',
                    intersect: false,
                },
                legend: { display: false },
                responsive: false,
                maintainAspectRatio: false
            }
        }
    },
    'seasonalVariationChart': {
        type: 'bar',
        data : {
            labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
            datasets: [{
                label: 'User journeys',
                data: [],
                borderColor: '#017E7E',
                backgroundColor: '#017E7E',
                fill: true,
                tension: 0
            }]
        },
        options : {
            scales: {
                x: {
                    type: 'category',
                    title: {
                        display: false,
                    }
                },
                y: {
                    display: false,
                    title: {
                        display: false,
                    }
                }
            },
            plugins: {
                tooltip: {
                    mode: 'index',
                    intersect: false,
                },
                legend: { display: false },
                responsive: false,
                maintainAspectRatio: false
            }
        }
    },
}

let options = {
    'timeSeriesChart' : {
        chart: {
            type: 'line'
        },
        stroke: {
            curve: 'smooth'
        },
        series: [{
            name: 'User journeys',
            data: [],
            color: '#017E7E'
        }],
        xaxis: {
            categories: [],
            type: 'datetime',
            labels: {
                datetimeFormatter: {
                    year: 'yyyy',
                    month: 'MMM yyyy',
                    day: 'dd MMM',
                    hour: 'HH:mm'
                }
            }
        }
    },
    'frequencyChart' : {
        chart: {
            type: 'area',
            toolbar: {
                show: false
            },
            zoom: {
                enabled: false
            },
            height: '125px'
        },
        stroke: {
            curve: 'smooth'
        },
        series: [{
            name: 'User journeys',
            data: [],
            color: '#017E7E'
        }],
        xaxis: {
            categories: [],
            type: 'datetime',
            labels: {
                datetimeFormatter: {
                    year: 'yyyy',
                    month: 'MMM yyyy',
                    day: 'dd MMM',
                    hour: 'HH:mm'
                }
            }
        },
        yaxis: {
            show: false
        },
        dataLabels: {
            enabled: false
        }
    },
    'dailyVariationChart' : {
        chart: {
            type: 'bar',
            toolbar: {
                show: false
            },
            zoom: {
                enabled: false
            },
            height: '125px'
        },
        stroke: {
            curve: 'smooth'
        },
        series: [{
            name: 'User journeys',
            color: '#017E7E',
            data: []
        }],
        xaxis: {
            categories: [],
            type: 'category'
        },
        yaxis: {
            show: false
        },
        dataLabels: {
            enabled: false
        }
    },
    'weeklyVariationChart' : {
        chart: {
            type: 'bar',
            toolbar: {
                show: false
            },
            zoom: {
                enabled: false
            },
            height: '125px'
        },
        stroke: {
            curve: 'smooth'
        },
        series: [{
            name: 'User journeys',
            color: '#017E7E',
            data: []
        }],
        xaxis: {
            categories: [],
            type: 'category'
        },
        yaxis: {
            show: false
        },
        dataLabels: {
            enabled: false
        }
    },
    'seasonalVariationChart' : {
        chart: {
            type: 'bar',
            toolbar: {
                show: false
            },
            zoom: {
                enabled: false
            },
            height: '125px'
        },
        stroke: {
            curve: 'smooth'
        },
        series: [{
            name: 'User journeys',
            color: '#017E7E',
            data: []
        }],
        xaxis: {
            categories: [],
            type: 'category'
        },
        yaxis: {
            show: false
        },
        dataLabels: {
            enabled: false
        }
    }
}

let variationFactor = {
    'daily': Array(24).fill(1),
    'weekly': Array(7).fill(1),
    'seasonal': Array(12).fill(1)
}

let adjustedVolumes = {
    'daily': Array(24).fill(1),
    'weekly': Array(7).fill(1),
    'seasonal': Array(12).fill(1)
}

function getTotalVolume(period_selected){
    let conversionRules = {
        'day': {'daily':1, 'weekly':7, 'seasonal':30, 'yearly':365},
        'week': {'daily':(1/7), 'weekly':1, 'seasonal':4 , 'yearly':52},
        'month': {'daily':(1/30), 'weekly':(1/4), 'seasonal':1, 'yearly':12},
        'year': {'daily':(1/365), 'weekly':(1/52), 'seasonal':(1/12), 'yearly':1}
    }
    let totalVolume = document.getElementById('form_add_avg_nb_usage_journey_value').value;
    let range = document.getElementById('form_add_avg_nb_usage_journey_range').value;
    return (totalVolume * conversionRules[range][period_selected]);
}

function getConversionRule(dateToCheck, periodTarget, periodToConvert){
    let conversionRule = 0;
    if(periodTarget === 'hour'){
        conversionRule = 24;
    }
    else if(periodTarget === 'day'){
        if(periodToConvert === 'year') {
            const isLeapYear = dateToCheck.isInLeapYear;
            conversionRule = isLeapYear ? 366 : 365;
        }else if(periodToConvert === 'week'){
            conversionRule = 7
        }else if(periodToConvert === 'month'){
            conversionRule = dateToCheck.daysInMonth;
        }
        else{
            conversionRule = 1
        }
    }else if(periodTarget === 'week'){
        if(periodToConvert === 'year') {
            conversionRule = dateToCheck.weeksInWeekYear;
        }else if(periodToConvert === 'month'){
            let lastDay = dateToCheck.endOf("month");
            let firstWeek = dateToCheck.weekNumber;
            let lastWeek = lastDay.weekNumber;
            conversionRule = lastWeek >= firstWeek ? lastWeek - firstWeek + 1 : (lastWeek + 52 - firstWeek + 1);
        }
        else{
            conversionRule = 1
        }
    }
    else if(periodTarget === 'month'){
        if(periodToConvert === 'year') {
            conversionRule = 12;
        }
        else{
            conversionRule = 1
        }
    }
    else{
        conversionRule = 1
    }
    return conversionRule;
}

function drawChart(chartName){
    let ctx = document.getElementById(chartName).getContext('2d');
    charts[chartName] = new Chart(ctx, {
        type: optionsChartJs[chartName].type,
        data: optionsChartJs[chartName].data,
        options: optionsChartJs[chartName].options
    });
}

function initChart(){
    variationChart('daily');
    variationChart('weekly');
    variationChart('seasonal');
    frequencyChart();
    timeSeriesChart();
}

function editFrequencyField(launchTimeSeriesChart = false){
    let userJourneyRange = document.getElementById('form_add_avg_nb_usage_journey_range');
    let selectedValue = userJourneyRange.value;
    let growthRateRange = document.getElementById('form_add_net_growth_rate_range');
    let optionsToCopy = userJourneyRange.querySelectorAll('option');
    let toCopy = false;
    growthRateRange.innerHTML = '';
    optionsToCopy.forEach(function(option){
        if(selectedValue === option.value){
            toCopy = true;
        }
        if(toCopy){
            let optionCopy = option.cloneNode(true);
            growthRateRange.appendChild(optionCopy);
        }
    });
    frequencyChart(launchTimeSeriesChart);
}

function variationController(periodVariation, launchTimeSeriesChart = false){
    const fromElements = Array.from(document.querySelectorAll(`[id^="form_add_from_${periodVariation}_variation_"]`));
    const toElements = Array.from(document.querySelectorAll(`[id^="form_add_to_${periodVariation}_variation_"]`));

    const intervals = fromElements.map((fromEl, i) => {
        const fromVal = parseInt(fromEl.value, 10);
        const toVal   = parseInt(toElements[i].value, 10);
        return {
            index: i,
            from: !isNaN(fromVal) ? fromVal : -1,
            to  : !isNaN(toVal)   ? toVal   : -1
        };
    });

    intervals.sort((a, b) => a.from - b.from);

    const usedHours = new Set();
    intervals.forEach(interval => {
        if (interval.from >= 0 && interval.to >= 0) {
            const start = Math.min(interval.from, interval.to);
            const end   = Math.max(interval.from, interval.to);
            for (let h = start; h <= end; h++) {
                usedHours.add(h);
            }
        }
    });

    intervals.forEach((current, i) => {
        const next = intervals[i + 1];
        const upperBound = next ? next.from : indexInput[periodVariation]['max'];
        const fromEl = fromElements[current.index];
        const toEl   = toElements[current.index];

        const mySlotHours = new Set();
        if (current.from >= 0 && current.to >= 0) {
            const myStart = Math.min(current.from, current.to);
            const myEnd   = Math.max(current.from, current.to);
            for (let h = myStart; h <= myEnd; h++) {
                mySlotHours.add(h);
            }
        }

        fromEl.querySelectorAll('option').forEach(option => {
            const hour = parseInt(option.value, 10);
            if (usedHours.has(hour) && !mySlotHours.has(hour)) {
                option.disabled = true;
            } else {
                option.disabled = false;
            }
        });

        toEl.querySelectorAll('option').forEach(option => {
            const hour = parseInt(option.value, 10);
            if (hour <= current.from || hour > upperBound) {
                option.disabled = true;
                return;
            }
            if (usedHours.has(hour) && !mySlotHours.has(hour)) {
                option.disabled = true;
            } else {
                option.disabled = false;
            }
        });

        const selectedToOption = toEl.options[toEl.selectedIndex];
        if (selectedToOption.disabled) {
            const firstValidOption = Array.from(toEl.options).find(option => !option.disabled);
            if (firstValidOption) {
                toEl.value = firstValidOption.value;
            } else {
                toEl.value = '';
            }
        }
    });
    variationChart(periodVariation, launchTimeSeriesChart);
}

function addTimeSlot(periodVariation){
    let optionsAlreadySelected =[];
    let rowToCopy = document.getElementById(periodVariation + '_variation_1');
    let elementVariations = document.querySelectorAll(`[id^="form_add_from_${periodVariation}_variation_"]`);

    elementVariations.forEach(function (element) {
        let from = document.getElementById(element.id).value;
        let to = document.getElementById(element.id.replace('from', 'to')).value;
        for (let i = parseInt(from); i < parseInt(to); i++){
            optionsAlreadySelected.push(parseInt(i));
        }
    });

    indexInput[periodVariation]['value'] += 1;
    let newId = parseInt(indexInput[periodVariation]['value']);
    let new_row = rowToCopy.cloneNode(true);
    new_row.id = periodVariation + '_variation_' + newId;

    let formElements = new_row.querySelectorAll('input, select');

    formElements.forEach(function (formElement) {
        let labelElement = new_row.querySelector('label[for="' + formElement.id + '"]');
        let idToReplace = formElement.id.split('_');
        let valueToSelected;
        if (optionsAlreadySelected.length > 0) {
            valueToSelected = Math.max(...optionsAlreadySelected) + 1;
        } else {
            valueToSelected = 0;
        }
        idToReplace[idToReplace.length - 1] = newId;

        if (formElement.id.startsWith('form_add_from_')){
            formElement.addEventListener('change', function () {
                variationController(periodVariation);
            });
        }

        if(formElement.id.startsWith('form_add_from_') || formElement.id.startsWith('form_add_to_')){
            let options = formElement.querySelectorAll('option');
            options.forEach(function(option){
                if(!optionsAlreadySelected.includes(parseInt(option.value)) ){
                    if(parseInt(option.value) === valueToSelected){
                        option.selected = true;
                    }
                }
            });
        }

        idToReplace = idToReplace.join('_');
        formElement.id = idToReplace;
        formElement.name = idToReplace;
        if (labelElement) {
            labelElement.htmlFor = idToReplace;
        }
    });

    document.getElementById(periodVariation + '_variation_bloc').appendChild(new_row);
    if (indexInput[periodVariation]['value'] === indexInput[periodVariation]['max']){
        document.getElementById('add_' + periodVariation + '_slot').classList.add('d-none');
    }
    variationController(periodVariation);
}

function createTimeSeriesChart(){
    let startDate = document.getElementById('form_add_timeframe_start_date').value;
    let netGrowRatePeriod = document.getElementById('form_add_net_growth_rate_range').value;
    let netGrowRateValue = document.getElementById('form_add_net_growth_rate_value').value;
    let avgNbUserJourneyPeriod = document.getElementById('form_add_avg_nb_usage_journey_range').value;
    let avgNbUserJourneyValue = document.getElementById('form_add_avg_nb_usage_journey_value').value;
    let timeframeValue = document.getElementById('form_add_timeframe_value').value;
    let timeframeRange = document.getElementById('form_add_timeframe_range').value;

    let timeseriesIndexWithVariations = [];
    let timeseriesValueWithVariations = [];

    let initDate = luxon.DateTime.local().startOf('year');
    let dateGrowth = luxon.DateTime.local().startOf('year')

    let growthRateDuration = luxon.Duration.fromObject({ [netGrowRatePeriod]: 1 });
    let timeframeDuration = luxon.Duration.fromObject({ [timeframeRange]: timeframeValue });
    let avgNbUserJourneyPeriodDuration = luxon.Duration.fromObject({ [avgNbUserJourneyPeriod]: 1 })

    // on calcule le volume total et on s'arrange pour que le base soit le jour
    let totalVolume = (avgNbUserJourneyValue / avgNbUserJourneyPeriodDuration.shiftTo('days').days) *
        growthRateDuration.shiftTo('days').days
    console.log(totalVolume);

    //on va d'abord appliquer le taux de croissance
    let volumeLooper = totalVolume
    for(let timeFrameUnit = 0; timeFrameUnit < timeframeValue; timeFrameUnit++){
        let dateLooper = initDate.plus({ [timeframeRange]: timeFrameUnit });
        for(let timeGrowthRateUnit=0; timeGrowthRateUnit < Math.round(timeframeDuration.shiftTo(netGrowRatePeriod+'s')[netGrowRatePeriod+'s']/timeframeValue); timeGrowthRateUnit++) {
            console.log(dateLooper.toISO(), volumeLooper);
            timeseriesIndexWithVariations.push(dateLooper.toISO());
            timeseriesValueWithVariations.push(volumeLooper);
            volumeLooper = volumeLooper + Math.round( parseInt(netGrowRateValue)/100 * volumeLooper);
            dateLooper = dateLooper.plus(growthRateDuration);
        }
    }

    console.log(timeseriesIndexWithVariations, timeseriesValueWithVariations);

    if(netGrowRatePeriod === 'year'){
        //on applique la variation seosonal
    }
    if(netGrowRatePeriod !== 'day'){
        //on applique la variation week
    }
    //on applique la variation daily

}

function applyVariation(timeseries, index, avgNbUserJourneyPeriod, netGrowRatePeriod, timeframe, timeframeValue){
    let periodToLuxonProp = {
        'hour':  'hours',
        'day':   'days',
        'week':  'weeks',
        'month': 'months',
        'year':  'years'
    };
    let keyPeriod = {
        'hour': 'daily',
        'day': 'weekly',
        'month': 'weekly',
        'year': 'seasonal',
    }
    const luxonProp = periodToLuxonProp[avgNbUserJourneyPeriod];
    const factorToApply = variationFactor[keyPeriod[avgNbUserJourneyPeriod]] || [];
    const numberOfParts = factorToApply.reduce((acc, cur) => acc + cur, 0);
    const avgNbUserJourneyPeriodTimeframe = luxon.Duration.fromObject({ [luxonProp]: 1 });

    const variationsValues = [];
    const variationsIndex  = [];

    for (let i = 0; i < index.length; i++) {
        let dateLooper = luxon.DateTime.fromISO(index[i]);
        const conversionRule = getConversionRule(dateLooper, avgNbUserJourneyPeriod, netGrowRatePeriod);
        const partValue = Math.round(timeseries[i] / numberOfParts);

        for (let j = 0; j < conversionRule; j++) {
            variationsIndex.push(dateLooper.toISO());
            variationsValues.push(partValue);
            dateLooper = dateLooper.plus(avgNbUserJourneyPeriodTimeframe);
        }
    }

    if (avgNbUserJourneyPeriod === 'year') {
        return applyVariation(variationsValues, variationsIndex, 'month', netGrowRatePeriod, timeframe, timeframeValue);
    } else if (avgNbUserJourneyPeriod === 'month' || avgNbUserJourneyPeriod === 'week') {
        return applyVariation(variationsValues, variationsIndex, 'day', netGrowRatePeriod, timeframe, timeframeValue);
    }
    else if(avgNbUserJourneyPeriod === 'day'){
        timeseriesToSave = applyVariation(variationsValues, variationsIndex, 'hour', netGrowRatePeriod, timeframe, timeframeValue);
    }

    return { variationsIndex, variationsValues };
}

function timeSeriesChart(){
    let timeRangeValue = parseInt(document.getElementById('form_add_timeframe_value').value);
    let timeRange = document.getElementById('form_add_timeframe_range').value;
    let frequency = optionsChartJs['frequencyChart']['data']['datasets'][0]['data']
    let index = optionsChartJs['frequencyChart']['data']['labels']
    let avgNbUserJourneyPeriod = document.getElementById('form_add_avg_nb_usage_journey_range').value;
    let netGrowRatePeriod = document.getElementById('form_add_net_growth_rate_range').value;
    let timeSeries = applyVariation(frequency, index, avgNbUserJourneyPeriod, netGrowRatePeriod, timeRange, timeRangeValue);
    updateTimeseriesChart();
}

function updateTimeseriesChart() {
    let periodAnalysis = document.getElementById('form_add_timeseries_period_analysis').value;
    let kpiAnalysis = document.getElementById('form_add_timeseries_kpi_analysis').value;
    let variationsIndex = timeseriesToSave.variationsIndex;
    let variationsValues = timeseriesToSave.variationsValues;
    let aggregatedIndex = [];
    let aggregatedValues = [];
    let currentGroup = [];
    let currentDate = luxon.DateTime.fromISO(variationsIndex[0]).startOf(periodAnalysis);

    let normalizedIndex = variationsIndex.map(date =>
        luxon.DateTime.fromISO(date).toUTC().toISO()
    );

    function reduceData(){
        if (currentGroup.length > 0) {
            aggregatedIndex.push(currentDate.toISO());
            if (kpiAnalysis === 'sum') {
                aggregatedValues.push(currentGroup.reduce((a, b) => a + b, 0)); // Calcul de la somme
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

    if (!charts['timeSeriesChart']) {
        drawChart('timeSeriesChart');
    }

    charts['timeSeriesChart'].data.datasets[0].label = `User journeys (${kpiAnalysis})`;
    charts['timeSeriesChart'].data.labels = aggregatedIndex;
    charts['timeSeriesChart'].data.datasets[0].data = aggregatedValues;
    charts['timeSeriesChart'].update();
}

function frequencyChart(launchTimeSeriesChart = false){
    let userJourneyValue  = parseInt(document.getElementById('form_add_avg_nb_usage_journey_value').value);
    let userJourneyRange  = document.getElementById('form_add_avg_nb_usage_journey_range').value;
    let growthRateRange   = document.getElementById('form_add_net_growth_rate_range').value;
    let timeframeValue    = parseInt(document.getElementById('form_add_timeframe_value').value);
    let timeframeRange    = document.getElementById('form_add_timeframe_range').value;

    let dateLooper = luxon.DateTime.local().startOf('year');
    let dateGrowth = luxon.DateTime.local().startOf('year');
    let growthRateFrame = luxon.Duration.fromObject({ [growthRateRange]: 1 });
    let timeframe = luxon.Duration.fromObject({ [timeframeRange]: timeframeValue });
    let periodStep = 0;
    let results = [];
    let labels = [];

    let dailyUserJourneyValue = 0;
    if (userJourneyRange !== 'day') {
        dailyUserJourneyValue = Math.ceil(
            userJourneyValue /
            luxon.Duration.fromObject({ [userJourneyRange]: 1 }).shiftTo('days').days
        );
    } else {
        dailyUserJourneyValue = userJourneyValue;
    }

    results.push(dailyUserJourneyValue.toFixed(2));
    labels.push(dateLooper.toFormat('yyyy-MM-dd'));

    while (periodStep < timeframe.shiftTo(growthRateRange)[`${growthRateRange}s`]-1) {
        dailyUserJourneyValue = Math.ceil(dailyUserJourneyValue * (1 + parseFloat(document.getElementById('form_add_net_growth_rate_value').value) / 100));
        dateGrowth = dateGrowth.plus(growthRateFrame);
        dateLooper = dateLooper.plus(growthRateFrame);
        results.push(dailyUserJourneyValue.toFixed(2));
        labels.push(dateLooper.toFormat('yyyy-MM-dd'));
        periodStep++;
    }

    optionsChartJs['frequencyChart'].data.labels = labels;
    optionsChartJs['frequencyChart'].data.datasets[0].data = results;
    optionsChartJs['frequencyChart'].options.scales.x.ticks.maxTicksLimit = timeframeValue;

    if (!charts['frequencyChart']) {
        drawChart('frequencyChart');
    } else {
        charts['frequencyChart'].data.labels = optionsChartJs['frequencyChart'].data.labels;
        charts['frequencyChart'].data.datasets[0].data = optionsChartJs['frequencyChart'].data.datasets[0].data;
        charts['frequencyChart'].update();
    }

    variationChart('daily');
    variationChart('weekly');
    variationChart('seasonal');
    if(launchTimeSeriesChart) {
        timeSeriesChart();
    }
}

function variationChart(periodVariation, launchTimeSeriesChart = false){
    adjustedVolumes[periodVariation] = Array(indexInput[periodVariation]['max']).fill(1);
    variationFactor[periodVariation] = Array(indexInput[periodVariation]['max']).fill(1);

    let totalVolume = getTotalVolume(periodVariation);
    let elementVariations = document.querySelectorAll('[id^="form_add_from_' + periodVariation + '_variation_"]');
    elementVariations.forEach(function (element) {
        let idx = element.id.split('_')[element.id.split('_').length - 1];
        let from = parseInt(document.getElementById('form_add_from_'+periodVariation+'_variation_' + idx).value);
        let to = parseInt(document.getElementById('form_add_to_'+periodVariation+'_variation_' + idx).value);
        let multiplier = parseInt(document.getElementById('form_add_multiplier_'+periodVariation+'_variation_' + idx).value);
        if (from !== to) {
            for (let slotTime = from; slotTime < to; slotTime++) {
                variationFactor[periodVariation][slotTime] = multiplier;
            }
        }
    });

    let numberOfParts = variationFactor[periodVariation].reduce((acc, cur) => acc + cur, 0);
    let partValue = Math.ceil(totalVolume / numberOfParts);

    for(let slotTime=0; slotTime < indexInput[periodVariation]['max'] ; slotTime++){
        adjustedVolumes[periodVariation][slotTime] = partValue * variationFactor[periodVariation][slotTime];
    }

    optionsChartJs[periodVariation+'VariationChart'].data.datasets[0].data =
    adjustedVolumes[periodVariation].map(value => value.toFixed(2));

    if (!charts[periodVariation+'VariationChart']) {
        drawChart(periodVariation+'VariationChart');
    } else {
        charts[periodVariation+'VariationChart'].data.datasets[0].data =
        optionsChartJs[periodVariation+'VariationChart'].data.datasets[0].data;
        charts[periodVariation+'VariationChart'].update();
    }

    if (launchTimeSeriesChart) {
    timeSeriesChart();
    }
}

document.getElementById('time-series-modal').addEventListener('shown.bs.modal', initChart);

function checkAttributes(usagePatternAttribute){
    if(usagePatternAttribute === 'timeseries'){
        document.getElementById('form_add_date_hourly_user_journey_starts').value= document.getElementById('form_add_timeframe_start_date').value;
        document.getElementById('form_add_list_hourly_user_journey_starts').value = timeseriesToSave['variationsValues'].toString();
    }else{
        document.getElementById('form_add_'+usagePatternAttribute).value = document.getElementById('form_select_'+usagePatternAttribute).value;
    }
    if(document.getElementById(usagePatternAttribute+'_icon_check').classList.contains('d-none')){
        document.getElementById(usagePatternAttribute+'_icon_check').classList.remove('d-none');
    }
}
