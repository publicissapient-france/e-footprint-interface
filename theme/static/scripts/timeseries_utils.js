function convertHourlyEmissionsByHardwareTypeFromStartDateToDailyDict(hardwareTypes, emissions) {
    let dailyEmissionsDataByHardwareType = {}

    for (const hardwareType of Object.keys(hardwareTypes)) {
        let values = emissions[hardwareType]['values']
        let startDate = luxon.DateTime.fromFormat(emissions[hardwareType]['start_date'], "yyyy-MM-dd HH:mm:ss",
            {zone: "utc"});
        let datesCorrespondingToValueTimestamps = [];
        for (let nbHoursSinceFirstValue = 0; nbHoursSinceFirstValue < values.length; nbHoursSinceFirstValue++) {
            datesCorrespondingToValueTimestamps.push(startDate.plus({hours: nbHoursSinceFirstValue}).toISODate());
        }
        dailyEmissionsDataByHardwareType[hardwareType] = datesCorrespondingToValueTimestamps.reduce(
            function (previousDict, dateAtIndex, index) {
                if (!previousDict[dateAtIndex]) {
                    previousDict[dateAtIndex] = 0;
                }
                previousDict[dateAtIndex] += values[index];
                return previousDict;
            },
            /* initial value of previousDict */
            {}
        )
    }
    return dailyEmissionsDataByHardwareType;
}

function cumulativeSumFromArray(input){
    let valueToCopy = [];
    let cumulative_sum = input[0];
    valueToCopy.push(cumulative_sum);
    for(let item=1; item < input.length; item++){
        cumulative_sum += input[item]
        valueToCopy.push(cumulative_sum)
    }
    return valueToCopy;
}

function getTimeIndexFromDataByHardwareTypeEmissions(startDate, granularity, nbValues){
    startDate = luxon.DateTime.fromFormat(startDate, "yyyy-MM-dd HH:mm:ss",{zone: "utc"});
    let labels = [];
    let dateLooper;
    let label;
    for(let nbValuesSinceStartDate = 0; nbValuesSinceStartDate < nbValues; nbValuesSinceStartDate++){
        dateLooper = startDate.plus({[granularity]: nbValuesSinceStartDate});
        if(granularity === "month"){
            label = `${dateLooper.year}-${String(dateLooper.month).padStart(2, "0")}`;
        }else{
            label = `${dateLooper.year}`;
        }
        labels.push(label);
    }
    return labels;
}

if (typeof module !== "undefined" && module.exports) {
    module.exports = {
        convertHourlyEmissionsByHardwareTypeFromStartDateToDailyDict,
        cumulativeSumFromArray,
        getTimeIndexFromDataByHardwareTypeEmissions
    };
}
