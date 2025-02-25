window.variationFactor = {
    'daily': Array(24).fill(1),
    'weekly': Array(7).fill(1),
    'seasonal': Array(12).fill(1)
}

window.adjustedVolumes = {
    'daily': Array(24).fill(1),
    'weekly': Array(7).fill(1),
    'seasonal': Array(12).fill(1)
}

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

function editFrequencyField(launchTimeSeriesChart = false){
    refreshFormValue();
    let avgNbUsageJourneyRange = window.formValues['avg_nb_usage_journey_range'];
    let netGrowthRateRange = window.formValues['net_growth_rate_range'];
    let optionsToCopy = avgNbUsageJourneyRange.querySelectorAll('option');
    let toCopy = false;
    netGrowthRateRange.innerHTML = '';
    optionsToCopy.forEach(function(option){
        if(parseInt(avgNbUsageJourneyRange.value) === parseInt(option.value)){
            toCopy = true;
        }
        if(toCopy){
            let optionCopy = option.cloneNode(true);
            netGrowthRateRange.appendChild(optionCopy);
        }
    });
    frequencyChart(launchTimeSeriesChart);
}

function variationController(periodVariation, launchTimeSeriesChart = false){
    const fromElements = Array.from(document.querySelectorAll(`[id^="from_${periodVariation}_variation_"]`));
    const toElements = Array.from(document.querySelectorAll(`[id^="to_${periodVariation}_variation_"]`));

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
        const upperBound = next ? next.from : window.indexInput[periodVariation]['max'];
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
    let elementVariations = document.querySelectorAll(`[id^="from_${periodVariation}_variation_"]`);

    elementVariations.forEach(function (element) {
        let from = document.getElementById(element.id).value;
        let to = document.getElementById(element.id.replace('from', 'to')).value;
        for (let i = parseInt(from); i < parseInt(to); i++){
            optionsAlreadySelected.push(parseInt(i));
        }
    });

    window.indexInput[periodVariation]['value'] += 1;
    let newId = parseInt(window.indexInput[periodVariation]['value']);
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

        if (formElement.id.startsWith('from_')){
            formElement.addEventListener('change', function () {
                variationController(periodVariation);
            });
        }

        if(formElement.id.startsWith('from_') || formElement.id.startsWith('to_')){
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
    if (window.indexInput[periodVariation]['value'] === window.indexInput[periodVariation]['max']){
        document.getElementById('add_' + periodVariation + '_slot').classList.add('d-none');
    }
    variationController(periodVariation);
}

function createTimeSeriesChart(){
    refreshFormValue();
    let timeframeStartDate = window.formValues['timeframe_start_date'].value;
    let netGrowthRateRange = window.formValues['net_growth_rate_range'].value;
    let netGrowRateValue = parseInt(window.formValues['net_growth_rate_value'].value);
    let avgNbUsageJourneyValue = parseInt(window.formValues['avg_nb_usage_journey_value'].value);
    let avgNbUsageJourneyRange = window.formValues['avg_nb_usage_journey_range'].value;
    let timeframeValue = parseInt(window.formValues['timeframe_value'].value);
    let timeframeRange = window.formValues['timeframe_range'].value;

    let variationsIndex = [];
    let variationsValues = [];
    let hourlyVariationsIndex = [];
    let hourlyVariationsValues = [];

    let luxonStartDate = luxon.DateTime.fromISO(timeframeStartDate);
    let luxonGrowthRateDuration = luxon.Duration.fromObject({ [netGrowthRateRange]: 1 });
    let luxonTimeframeDuration = luxon.Duration.fromObject({ [timeframeRange]: timeframeValue });
    let luxonAvgNbUsageJourneyRange = luxon.Duration.fromObject({ [avgNbUsageJourneyRange]: 1 });

    let ratioDay = (luxonStartDate.plus(luxonGrowthRateDuration).diff(luxonStartDate, 'days').days)/luxonAvgNbUsageJourneyRange.shiftTo('days').days;

    let volumeLooper = avgNbUsageJourneyValue * ratioDay;
    for(let timeFrameUnit = 0; timeFrameUnit < timeframeValue; timeFrameUnit++){
        let dateLooper = luxonStartDate.plus({ [timeframeRange]: timeFrameUnit });
        for(let timeGrowthRateUnit=0; timeGrowthRateUnit < Math.round(luxonTimeframeDuration.shiftTo(netGrowthRateRange+'s')[netGrowthRateRange+'s']/timeframeValue); timeGrowthRateUnit++) {
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
}
