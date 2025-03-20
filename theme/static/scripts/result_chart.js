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
                    type: 'time',
                    time: {
                        tooltipFormat: 'yyyy',
                        unit: 'year'
                    },
                    title: { display: false },
                    grid: { display: false }
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

    let labels = [];
    let aggregated_emissions_data = {}

    for (const hardwareType of Object.keys(dataByHardwareType)) {
        let values = emissions[hardwareType]['values']
        let startDate = luxon.DateTime.fromFormat(emissions[hardwareType]['start_date'], "yyyy-MM-dd HH:mm:ss",
            { zone: "utc" });
        let datesCorrespondingToValueTimestamps = [];
        for(let nbHoursSinceFirstValue = 0; nbHoursSinceFirstValue < values.length; nbHoursSinceFirstValue++) {
            datesCorrespondingToValueTimestamps.push(startDate.plus({ hours: nbHoursSinceFirstValue }).toISODate());
        }
        let dailyDateValueSumDict = datesCorrespondingToValueTimestamps.reduce(
            function(previousDict, dateAtIndex, index){
                if (!previousDict[dateAtIndex]) {
                    previousDict[dateAtIndex] = 0;
                }
                previousDict[dateAtIndex] += values[index];
                return previousDict;
            },
            /* initial value of previousDict */
            {}
        );
        aggregated_emissions_data[hardwareType] = sumDailyValuesByDisplayGranularity(
            dailyDateValueSumDict, resultsTemporalGranularity);
        let value_to_copy = Object.values(aggregated_emissions_data[hardwareType]);
        if(chartType=='bar'){
            dataByHardwareType[hardwareType]["data"].push(...value_to_copy);
        }else{
            let cumulative_sum = value_to_copy[0];
            for(let item=1; item < value_to_copy.length; item++){
                cumulative_sum += value_to_copy[item]
                dataByHardwareType[hardwareType]["data"].push(cumulative_sum)
            }
        }
    }

    labels = Object.keys(aggregated_emissions_data['Servers_and_storage_energy']);
    let chartData = {labels: labels, datasets: []}

    for (const hardwareType of Object.keys(dataByHardwareType)) {
        chartData["datasets"].push(dataByHardwareType[hardwareType]);
    }

    config["data"] = chartData;
    config["type"] = chartType;

    config.options.scales.x.time.unit = resultsTemporalGranularity === "month" ? "month" : "year";
    config.options.scales.x.time.tooltipFormat = resultsTemporalGranularity === "month" ? "MMM yyyy" : "yyyy";

    if (window.charts[chartType+'Chart']) {
        window.charts[chartType+'Chart'].destroy();
        window.charts[chartType+'Chart'] = null;
    }

    let area_ctx = document.getElementById(chartType + "Chart").getContext("2d");

    window.charts[chartType+'Chart'] = new Chart(area_ctx, config);
}

function drawBarResultChart(){
    let resultsTemporalGranularity = document.getElementById('results_temporal_granularity').value;
    updateAreaResultChart('bar', resultsTemporalGranularity);
}
