function updateAreaResultChart(chartType, resultsTemporalGranularity){
    let config = {
        chart:{
            height: '400px',
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: "bottom",
                },
                title: {
                    display: true,
                    text: 'Total CO2 emissions in metric tons',
                    color: "rgb(107,114,128)"
                },
                tooltip: {
                    mode: "index",
                    intersect: false,
                },
            },
            scales: {
                x: {
                    stacked: true,
                    title: {
                        display: true,
                        text: "Years",
                        color: "rgb(107,114,128)",
                        align: 'start'
                    },
                },
                y: {
                    stacked: true,
                    title: {
                        display: true,
                        text: "Total CO2 emissions in metric tons",
                        color: "rgb(107,114,128)"
                    },
                },
            },
        },
    }

    let dataByHardwareType = {
        'Servers_and_storage_energy': {
            label: "Servers and storage usage",
            backgroundColor: "#C6FFF9",
        },
        'Devices_energy': {
            label: "Devices usage",
            backgroundColor: "#44E0D9",
        },
        'Network_energy': {
            label: "Network usage",
            backgroundColor: "#00A3A1",
        },
        'Servers_and_storage_fabrication': {
            label: "Servers and storage fabrication",
            backgroundColor: "#DEECF8",
        },
        'Devices_fabrication': {
            label: "Devices fabrication",
            backgroundColor: "#A3CDED",
        }
    }

    for (const hardwareType of Object.keys(dataByHardwareType)) {
        if (chartType === "line") {
            dataByHardwareType[hardwareType]["borderWidth"] = 1;
            dataByHardwareType[hardwareType]["fill"] = true;
            dataByHardwareType[hardwareType]["data"] = [0];
        }else {
            dataByHardwareType[hardwareType]["data"] = [];
        }
    }

    let startDate = luxon.DateTime.fromFormat(emissions['Servers_and_storage_energy']['start_date'], "yyyy-MM-dd HH:mm:ss");
    let nbElements = emissions['Servers_and_storage_energy']['values'].length
    let endDate = startDate.plus(luxon.Duration.fromObject({ hours: nbElements }));
    let resultsTemporalGranularityDuration = luxon.Duration.fromObject({ [resultsTemporalGranularity]: 1 });
    let labels = [];
    let rawValuesIndex = 0;
    let computedValuesIndex = 0;
    if (chartType === "line") {
        labels.push(startDate.toISODate());
        computedValuesIndex += 1;
    }

    while (startDate.plus(resultsTemporalGranularityDuration) <= endDate){
        let nextDate = startDate.plus(resultsTemporalGranularityDuration);
        let nbHours = nextDate.diff(startDate, 'hours').hours;
        let limitIndex = rawValuesIndex + nbHours;
        for (const hardwareType of Object.keys(dataByHardwareType)) {
            let sumOverPeriod = 0;
            for (let i = rawValuesIndex; i < limitIndex; i++){
                if (i < emissions[hardwareType]['values'].length){
                    sumOverPeriod += emissions[hardwareType]['values'][i];
                }
            }
            // Convert to metric tons
            sumOverPeriod = sumOverPeriod / 1000;
            if (chartType === "line") {
                let previousCumulativeValue = dataByHardwareType[hardwareType]["data"][computedValuesIndex - 1];
                dataByHardwareType[hardwareType]["data"].push(sumOverPeriod + previousCumulativeValue);
            }else{
                dataByHardwareType[hardwareType]["data"].push(sumOverPeriod);
            }
        }
        if (chartType === "line") {
            labels.push(nextDate.toISODate());
        }else{
            labels.push(startDate.toISODate() + " to " + nextDate.toISODate());
        }
        rawValuesIndex += nbHours;
        computedValuesIndex += 1;
        startDate = nextDate;
    }

    let chartData = {labels: labels, datasets: []}

    for (const hardwareType of Object.keys(dataByHardwareType)) {
        chartData["datasets"].push(dataByHardwareType[hardwareType]);
    }

    config["data"] = chartData;
    config["type"] = chartType;

    let area_ctx = document.getElementById(chartType + "Chart").getContext("2d");
    if(window.charts[chartType] == null){
        window.charts[chartType] = new Chart(area_ctx, config);
    }else{
        window.charts[chartType].data = chartData;
        window.charts[chartType].update();
    }
}

function drawAreaResultChart(){
    let resultsTemporalGranularity = document.getElementById('results_temporal_granularity').value;
    updateAreaResultChart('line', resultsTemporalGranularity);
}
