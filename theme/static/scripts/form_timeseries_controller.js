function editFrequencyField(){
    let initialUsageJourneyVolumeTimespan = document.getElementById('initial_usage_journey_volume_timespan');
    let netGrowthRateTimespan = document.getElementById('net_growth_rate_timespan');
    let optionsToCopy = initialUsageJourneyVolumeTimespan.querySelectorAll('option');
    let toCopy = false;
    netGrowthRateTimespan.innerHTML = '';
    optionsToCopy.forEach(function(option){
        if(initialUsageJourneyVolumeTimespan.value === option.value){
            toCopy = true;
        }
        if(toCopy){
            let optionCopy = option.cloneNode(true);
            netGrowthRateTimespan.appendChild(optionCopy);
        }
    });
    createTimeSeriesChart();
}

function createTimeSeriesChart(){
    let startDate = document.getElementById('start_date').value;
    let modelingDurationValue = parseInt(document.getElementById('modeling_duration_value').value);
    let modelingDurationUnit = document.getElementById('modeling_duration_unit').value;
    let netGrowRateInPercentage = parseInt(document.getElementById('net_growth_rate_in_percentage').value);
    let netGrowthRateTimespan = document.getElementById('net_growth_rate_timespan').value;
    let initialUsageJourneyVolume = parseInt(document.getElementById('initial_usage_journey_volume').value);
    let initialUsageJourneyVolumeTimespan = document.getElementById('initial_usage_journey_volume_timespan').value;

    window.dailyUsageJourneyVolume = {};

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
    let dailyUsageJourneyVolume = firstDailyUsageJourneyVolume;
    for(let day_nb = 0; day_nb < modelingDurationInDays; day_nb++){
        window.dailyUsageJourneyVolume[dateLooper.toISO()] = dailyUsageJourneyVolume;
        dailyUsageJourneyVolume *= dailyGrowthRate;
        dateLooper = luxonStartDate.plus({ ["day"]: (day_nb+1)});
    }
    updateTimeseriesChart();
}
