function sumDailyValuesByDisplayGranularity(dailyValues, displayGranularity) {
    let aggregatedData = {};
    Object.keys(dailyValues).forEach((date, index) => {
        let dateObj = luxon.DateTime.fromISO(date);
        let key;

        if (displayGranularity === "month") {
            key = `${dateObj.year}-${String(dateObj.month).padStart(2, "0")}`;
        } else if (displayGranularity === "year") {
            key = `${dateObj.year}`;
        } else {
            key = date;
        }
        if (!aggregatedData[key]) {
            aggregatedData[key] = 0;
        }
        aggregatedData[key] += dailyValues[date];
    });

    return aggregatedData;
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

function generateTimeIndexLabels(startDate, granularity, nbValues){
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
        sumDailyValuesByDisplayGranularity,
        cumulativeSumFromArray,
        generateTimeIndexLabels
    };
}
