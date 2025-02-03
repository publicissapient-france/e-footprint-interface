window.charts = {
    'stackedAreaChart' : null,
    'stackedBarChart' : null
};

function updateAreaResultChart(chart, periodToApplied, kpiToCalculate){

    let data = {
        'stackedAreaChart' : {
            labels: ["0", "y1", "y2", "y3", "y4", "y5"],
            datasets: [
            {
                label: "Server usage",
                data: [0, 0.02, 0.04, 0.06, 0.08, 0.1],
                backgroundColor: "rgba(176, 228, 246, 0.8)",
                borderWidth: 1,
                fill: true,
            },
            {
                label: "Devices usage",
                data: [0, 0.03, 0.06, 0.09, 0.12, 0.15],
                backgroundColor: "rgba(124, 205, 224, 0.8)",
                borderWidth: 1,
                fill: true,
            },
            {
                label: "Network usage",
                data: [0, 0.05, 0.1, 0.15, 0.2, 0.25],
                backgroundColor: "rgba(100, 181, 192, 0.8)",
                borderWidth: 1,
                fill: true,
            },
            {
                label: "Servers fabrication",
                data: [0, 0.01, 0.02, 0.03, 0.04, 0.05],
                backgroundColor: "rgba(162, 210, 255, 0.8)",
                borderWidth: 1,
                fill: true,
            },
            {
                label: "Devices fabrication",
                data: [0, 0.015, 0.03, 0.045, 0.06, 0.075],
                backgroundColor: "rgba(220, 235, 255, 0.8)",
                borderWidth: 1,
                fill: true,
            },
        ],
        },
        'stackedBarChart' : {
    labels: ["y1", "y2", "y3", "y4", "y5"],
    datasets: [
        {
            label: "Server usage",
            data: emissions['Servers_energy']['values'],
            backgroundColor: "rgba(176, 228, 246, 0.8)",
        },
        {
            label: "Devices usage",
            data: emissions['Devices_energy']['values'],
            backgroundColor: "rgba(124, 205, 224, 0.8)",
        },
        {
            label: "Network usage",
            data: emissions['Network_energy']['values'],
            backgroundColor: "rgba(100, 181, 192, 0.8)",
        },
        {
            label: "Servers fabrication",
            data: emissions['Servers_fabrication']['values'],
            backgroundColor: "rgba(162, 210, 255, 0.8)",
        },
        {
            label: "Devices fabrication",
            data: emissions['Devices_fabrication']['values'],
            backgroundColor: "rgba(220, 235, 255, 0.8)",
        },
    ],
}
}

    let config = {
        'stackedAreaChart' : {
        chart:{
            height: '400px',
        },
        type: "line",
        data: data['stackedAreaChart'],
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: "bottom",
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
                    },
                },
                y: {
                    stacked: true,
                    title: {
                        display: true,
                        text: "Total tons of CO2 emissions",
                    },
                },
            },
        },
    },
        'stackedBarChart' : {
        chart:{
            height: '400px',
        },
        type: "bar",
        data: data['stackedBarChart'],
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: "bottom",
                },
                title: {
                    display: true,
                    text: 'Total tons of CO2 emissions',
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
                        text: "Total tons of CO2 emissions",
                        color: "rgb(107,114,128)"
                    },
                },
            },
        },
    }
    }

    let dataNameKPI = ['Servers_energy', 'Devices_energy', 'Network_energy', 'Servers_fabrication', 'Devices_fabrication'];
    let dataKPI = {
        'Servers_energy' : [],
        'Devices_energy' : [],
        'Network_energy' : [],
        'Servers_fabrication' : [],
        'Devices_fabrication' : []};
    let startDate = luxon.DateTime.fromFormat(emissions['Servers_energy']['start_date'], "yyyy-MM-dd HH:mm:ss");
    let nbElement = emissions['Servers_energy']['values'].length
    let endDate = startDate.plus(luxon.Duration.fromObject({ hours: nbElement }));
    let periodToAppliedFrame = luxon.Duration.fromObject({ [periodToApplied]: 1 });
    let labels = [];
    let index = 0;

    let cumsumValues = {
        'Servers_energy': 0,
        'Devices_energy': 0,
        'Network_energy': 0,
        'Servers_fabrication': 0,
        'Devices_fabrication': 0
    };

    while (startDate < endDate){
        let nextDate = startDate.plus(periodToAppliedFrame);
        labels.push(startDate.toISODate());
        let nbHours = Math.min(nextDate.diff(startDate, 'hours').hours, nbElement - index);
        let limitIndex = index + nbHours;
        dataNameKPI.forEach(name => {
            let value_kpi = 0;
            for (let i = index; i < limitIndex; i++){
                value_kpi += emissions[name]['values'][i];
            }
            if(kpiToCalculate === 'avg'){
                dataKPI[name].push(value_kpi/nbHours);
            }else if(kpiToCalculate === 'sum'){
                dataKPI[name].push(value_kpi);
            }else{
                cumsumValues[name] += value_kpi;
                dataKPI[name].push(cumsumValues[name]);
            }
        });
        index += nbHours;
        startDate = nextDate;
    }

    dataNameKPI.forEach(name => {
        data[chart].datasets[dataNameKPI.indexOf(name)].data = dataKPI[name];
    });
    data[chart].labels = labels;
    let area_ctx = document.getElementById(chart).getContext("2d");
    if(window.charts[chart] == null){

        window.charts[chart] = new Chart(area_ctx, config[chart]);
    }else{
        dataNameKPI.forEach(name => {
            window.charts[chart].data.datasets[dataNameKPI.indexOf(name)].label = "Total tons of CO2 emissions";
            window.charts[chart].data.datasets[dataNameKPI.indexOf(name)].data = dataKPI[name];
            window.charts[chart].data.labels = labels;
        });
        window.charts[chart].update();
    }
}

function drawAreaResultChart(){
    let periodToApplied = document.getElementById('result_period_analysis').value;
    let kpiToCalculate = document.getElementById('result_kpi_analysis').value;
    updateAreaResultChart('stackedAreaChart', periodToApplied, kpiToCalculate);
}
