window.config = {
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
                offset: true,
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

window.dataByHardwareType = {
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

function updateAreaResultChart(chartType, resultsTemporalGranularity){
    let chartData = {labels: [], datasets: []}

    for (const hardwareType of Object.keys(window.dataByHardwareType)) {
        if (chartType === "line") {
            window.dataByHardwareType[hardwareType]["borderWidth"] = 1;
            window.dataByHardwareType[hardwareType]["fill"] = true;
            window.dataByHardwareType[hardwareType]["data"] = [];
        }else {
            window.dataByHardwareType[hardwareType]["data"] = [];
        }
    }

    let hardwareTypeDailyEmissions = convertHourlyEmissionsByHardwareTypeFromStartDateToDailyDict(
        window.dataByHardwareType, window.emissions
    )

    for (const hardwareType of Object.keys(hardwareTypeDailyEmissions)) {
        let value_to_copy = Object.values(
            sumDailyValuesByDisplayGranularity(hardwareTypeDailyEmissions[hardwareType], resultsTemporalGranularity));
        if(chartType === "line"){
            value_to_copy = cumulativeSumFromArray(value_to_copy)
        }
        window.dataByHardwareType[hardwareType]["data"] = value_to_copy;
    }

    chartData.labels = getTimeIndexFromDataByHardwareTypeEmissions(
        window.emissions['Servers_and_storage_energy']['start_date'],resultsTemporalGranularity,
        window.dataByHardwareType['Servers_and_storage_energy']["data"].length);

    for (const hardwareType of Object.keys(window.dataByHardwareType)) {
        chartData["datasets"].push(window.dataByHardwareType[hardwareType]);
    }

    window.config["data"] = chartData;
    window.config["type"] = chartType;

    window.config.options.scales.x.time.unit = resultsTemporalGranularity === "month" ? "month" : "year";
    window.config.options.scales.x.time.tooltipFormat = resultsTemporalGranularity === "month" ? "MMM yyyy" : "yyyy";

    if (window.charts[chartType+'Chart']) {
        window.charts[chartType+'Chart'].destroy();
        window.charts[chartType+'Chart'] = null;
    }

    let area_ctx = document.getElementById(chartType + "Chart").getContext("2d");

    window.charts[chartType+'Chart'] = new Chart(area_ctx, window.config);
}

function drawBarResultChart(){
    let resultsTemporalGranularity = document.getElementById('results_temporal_granularity').value;
    updateAreaResultChart('bar', resultsTemporalGranularity);
}
