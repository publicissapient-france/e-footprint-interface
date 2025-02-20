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

function editFrequencyField(){
    refreshFormValue();
    let avgNbUsageJourneyPeriod = window.formValues['modal_avg_nb_usage_journey_period'];
    let netGrowthRatePeriod = window.formValues['modal_net_growth_rate_period'];
    let optionsToCopy = avgNbUsageJourneyPeriod.querySelectorAll('option');
    let toCopy = false;
    netGrowthRatePeriod.innerHTML = '';
    optionsToCopy.forEach(function(option){
        if(avgNbUsageJourneyPeriod.value === option.value){
            toCopy = true;
        }
        if(toCopy){
            let optionCopy = option.cloneNode(true);
            netGrowthRatePeriod.appendChild(optionCopy);
        }
    });
    createTimeSeriesChart();
}

function createTimeSeriesChart(){
    refreshFormValue();
    let timeframeStartDate = window.formValues['modal_timeframe_start_date'].value;
    let netGrowthRatePeriod = window.formValues['modal_net_growth_rate_period'].value;
    let netGrowRateValue = parseInt(window.formValues['modal_net_growth_rate_value'].value);
    let avgNbUsageJourneyValue = parseInt(window.formValues['modal_avg_nb_usage_journey_value'].value);
    let avgNbUsageJourneyPeriod = window.formValues['modal_avg_nb_usage_journey_period'].value;
    let timeframeValue = parseInt(window.formValues['modal_timeframe_value'].value);
    let timeframeRange = window.formValues['modal_timeframe_range'].value;

    window.variationsIndex = [];
    window.variationsValues = [];

    let luxonStartDate = luxon.DateTime.fromISO(timeframeStartDate);
    let luxonGrowthRateDuration = luxon.Duration.fromObject({ [netGrowthRatePeriod]: 1 });
    let luxonTimeframeDuration = luxon.Duration.fromObject({ [timeframeRange]: timeframeValue });

    let nbStep = luxonTimeframeDuration.shiftTo(netGrowthRatePeriod+'s')[netGrowthRatePeriod+'s'];

    let dateLooper = luxonStartDate;
    for(let step = 0; step < nbStep; step++){
        window.variationsIndex.push(dateLooper.toISO());
        window.variationsValues.push(avgNbUsageJourneyValue*luxonGrowthRateDuration.shiftTo(avgNbUsageJourneyPeriod+'s')[avgNbUsageJourneyPeriod+'s']);
        avgNbUsageJourneyValue *= (1 + netGrowRateValue/100);
        dateLooper = luxonStartDate.plus({ [netGrowthRatePeriod]: (step+1) });
    }
    updateTimeseriesChart();
}
