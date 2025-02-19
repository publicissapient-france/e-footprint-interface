function refreshFormValue(){
    window.formValues = {
        'timeframe_start_date': document.getElementById('timeframe_start_date'),
        'net_growth_rate_period': document.getElementById('net_growth_rate_period'),
        'net_growth_rate_value': document.getElementById('net_growth_rate_value'),
        'avg_nb_usage_journey_value': document.getElementById('avg_nb_usage_journey_value'),
        'avg_nb_usage_journey_period': document.getElementById('avg_nb_usage_journey_period'),
        'timeframe_value': document.getElementById('timeframe_value'),
        'timeframe_range': document.getElementById('timeframe_range')
    }
}

function editFrequencyField(){
    refreshFormValue();
    let avgNbUsageJourneyPeriod = window.formValues['avg_nb_usage_journey_period'];
    let netGrowthRatePeriod = window.formValues['net_growth_rate_period'];
    let optionsToCopy = avgNbUsageJourneyPeriod.querySelectorAll('option');
    let toCopy = false;
    netGrowthRatePeriod.innerHTML = '';
    optionsToCopy.forEach(function(option){
        if(parseInt(avgNbUsageJourneyPeriod.value) === parseInt(option.value)){
            toCopy = true;
        }
        if(toCopy){
            let optionCopy = option.cloneNode(true);
            netGrowthRatePeriod.appendChild(optionCopy);
        }
    });
    updateTimeseriesChart();
}

function createTimeSeriesChart(){
    refreshFormValue();
    let timeframeStartDate = window.formValues['timeframe_start_date'].value;
    let netGrowthRatePeriod = window.formValues['net_growth_rate_period'].value;
    let netGrowRateValue = parseInt(window.formValues['net_growth_rate_value'].value);
    let avgNbUsageJourneyValue = parseInt(window.formValues['avg_nb_usage_journey_value'].value);
    let avgNbUsageJourneyPeriod = window.formValues['avg_nb_usage_journey_period'].value;
    let timeframeValue = parseInt(window.formValues['timeframe_value'].value);
    let timeframeRange = window.formValues['timeframe_range'].value;

    let variationsIndex = [];
    let variationsValues = [];
    let hourlyVariationsIndex = [];
    let hourlyVariationsValues = [];

    let luxonStartDate = luxon.DateTime.fromISO(timeframeStartDate);
    let luxonGrowthRateDuration = luxon.Duration.fromObject({ [netGrowthRatePeriod]: 1 });
    let luxonTimeframeDuration = luxon.Duration.fromObject({ [timeframeRange]: timeframeValue });
    let luxonAvgNbUsageJourneyRange = luxon.Duration.fromObject({ [avgNbUsageJourneyPeriod]: 1 });

    let ratioDay = (luxonStartDate.plus(luxonGrowthRateDuration).diff(luxonStartDate, 'days').days)/luxonAvgNbUsageJourneyRange.shiftTo('days').days;

    let volumeLooper = avgNbUsageJourneyValue * ratioDay;
    for(let timeFrameUnit = 0; timeFrameUnit < timeframeValue; timeFrameUnit++){
        let dateLooper = luxonStartDate.plus({ [timeframeRange]: timeFrameUnit });
        for(let timeGrowthRateUnit=0; timeGrowthRateUnit < Math.round(luxonTimeframeDuration.shiftTo(netGrowthRatePeriod+'s')[netGrowthRatePeriod+'s']/timeframeValue); timeGrowthRateUnit++) {
            variationsIndex.push(dateLooper.toISO());
            variationsValues.push(volumeLooper);
            volumeLooper *=  (1 + netGrowRateValue/100);
            dateLooper = dateLooper.plus(luxonGrowthRateDuration);
        }
    }

    let indexDay = 0
    variationsIndex.forEach((row) => {
        let indexDate = luxon.DateTime.fromISO(row);
        let nbDays = indexDate.plus(luxonGrowthRateDuration).diff(indexDate, 'days').days;
        let convertedValue = Math.round(variationsValues[indexDay]/nbDays);
        for (let day = 0; day < nbDays; day++) {
            let dayDate = indexDate.plus({days: day});
            for(let hour=0; hour < 24; hour++){
                hourlyVariationsIndex.push(dayDate.plus({hours: hour}).toISO());
                hourlyVariationsValues.push(convertedValue/24);
            }
        }
        indexDay += 1;
    });
    window.variationsIndex = hourlyVariationsIndex;
    window.variationsValues = hourlyVariationsValues;
    window.timeseriesToSave = { hourlyVariationsIndex, hourlyVariationsValues };
    updateTimeseriesChart();
}
