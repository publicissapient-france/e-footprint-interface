function editFrequencyField(){
    let occurrencePeriodUsageJourney = document.getElementById('modal_avg_nb_usage_journey_period');
    let netGrowthRateDurationUnit = document.getElementById('modal_net_growth_rate_period');
    let optionsToCopy = occurrencePeriodUsageJourney.querySelectorAll('option');
    let toCopy = false;
    netGrowthRateDurationUnit.innerHTML = '';
    optionsToCopy.forEach(function(option){
        if(occurrencePeriodUsageJourney.value === option.value){
            toCopy = true;
        }
        if(toCopy){
            let optionCopy = option.cloneNode(true);
            netGrowthRateDurationUnit.appendChild(optionCopy);
        }
    });
    createTimeSeriesChart();
}

function createTimeSeriesChart(){
    let timeframeStartDate = document.getElementById('modal_timeframe_start_date').value;
    let timeframeDurationValue = parseInt(document.getElementById('modal_timeframe_value').value);
    let timeframeDurationUnit = document.getElementById('modal_timeframe_range').value;

    let netGrowthRateDurationUnit = document.getElementById('modal_net_growth_rate_period').value;
    let netGrowRateFactorValue = parseInt(document.getElementById('modal_net_growth_rate_value').value);

    let volumeUsageJourney = parseInt(document.getElementById('modal_avg_nb_usage_journey_value').value);
    let occurrencePeriodUsageJourney = document.getElementById('modal_avg_nb_usage_journey_period').value;

    window.variationsIndex = [];
    window.variationsValues = [];

    let luxonStartDate = luxon.DateTime.fromISO(timeframeStartDate);
    let luxonNetGrowthRateDuration = luxon.Duration.fromObject({ [netGrowthRateDurationUnit]: 1 });
    let luxonTimeframeDuration = luxon.Duration.fromObject({ [timeframeDurationUnit]: timeframeDurationValue });

    let timeOccurrenceBasedOnNetGrowthRateDurationUnit = luxonTimeframeDuration.shiftTo(netGrowthRateDurationUnit+'s')[netGrowthRateDurationUnit+'s'];

    let dateLooper = luxonStartDate;
    for(let step = 0; step < timeOccurrenceBasedOnNetGrowthRateDurationUnit; step++){
        window.variationsIndex.push(dateLooper.toISO());
        let valueToPush =  volumeUsageJourney*luxonNetGrowthRateDuration.shiftTo(occurrencePeriodUsageJourney+'s')[occurrencePeriodUsageJourney+'s']
        window.variationsValues.push(valueToPush);
        volumeUsageJourney *= (1 + netGrowRateFactorValue/100);
        dateLooper = luxonStartDate.plus({ [netGrowthRateDurationUnit]: (step+1) });
    }
    updateTimeseriesChart();
}
