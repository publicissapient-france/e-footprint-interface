const { computeUsageJourneyVolume, sumUsageJourneyVolumeByDisplayGranularity } = require('../theme/static/scripts/timeseries.js');
const { DateTime, Duration } = require("luxon");
global.luxon = { DateTime, Duration };

let startDate = '2021-01-01';
let modelingDurationValue = 1;
let modelingDurationUnit = 'year';
let netGrowRateInPercentage = 10;
let netGrowthRateTimespan = 'month';
let initialUsageJourneyVolume = 1000;
let initialUsageJourneyVolumeTimespan = 'month';
let testDailyUsageJourneyVolume = computeUsageJourneyVolume(
    startDate,
    modelingDurationValue,
    modelingDurationUnit,
    netGrowRateInPercentage,
    netGrowthRateTimespan,
    initialUsageJourneyVolume,
    initialUsageJourneyVolumeTimespan
)

test(
    'computeUsageJourneyVolume_check_length_return_value', () => {
    let dailyUsageJourneyVolume = computeUsageJourneyVolume(
        startDate,
        modelingDurationValue,
        modelingDurationUnit,
        netGrowRateInPercentage,
        netGrowthRateTimespan,
        initialUsageJourneyVolume,
        initialUsageJourneyVolumeTimespan
    )
    expect(Object.keys(dailyUsageJourneyVolume).length).toBe(365);
});

/*
With luxon when a month is shifted in days, 1 month equal to 30 days
 */
test(
    'computeUsageJourneyVolume_check_first_value_monthly', () => {
        let dailyUsageJourneyVolume = computeUsageJourneyVolume(
            startDate,
            modelingDurationValue,
            modelingDurationUnit,
            netGrowRateInPercentage,
            netGrowthRateTimespan,
            initialUsageJourneyVolume,
            initialUsageJourneyVolumeTimespan
        )
        let firstDay = Object.keys(dailyUsageJourneyVolume)[0];
        let computedValue = dailyUsageJourneyVolume[firstDay];
        let expectedValue = 1000 / 30;
        expect(computedValue).toBeCloseTo(expectedValue, 2);
    }
)

/*
With luxon when a year  is shifted in days, 1 year equal to 365 days
 */
test(
    'computeUsageJourneyVolume_check_first_value_yearly', () => {
        initialUsageJourneyVolumeTimespan = 'year';
        let dailyUsageJourneyVolume = computeUsageJourneyVolume(
            startDate,
            modelingDurationValue,
            modelingDurationUnit,
            netGrowRateInPercentage,
            netGrowthRateTimespan,
            initialUsageJourneyVolume,
            initialUsageJourneyVolumeTimespan
        )
        let firstDay = Object.keys(dailyUsageJourneyVolume)[0];
        let computedValue = dailyUsageJourneyVolume[firstDay];
        let expectedValue = 1000 / 365;
        expect(computedValue).toBeCloseTo(expectedValue, 2);
    }
)

test(
    'computeUsageJourneyVolume_check_growth_rate_monthly', () => {
        let netGrowRateInPercentage = 20;
        let dailyUsageJourneyVolume = computeUsageJourneyVolume(
            startDate,
            modelingDurationValue,
            modelingDurationUnit,
            netGrowRateInPercentage,
            netGrowthRateTimespan,
            initialUsageJourneyVolume,
            initialUsageJourneyVolumeTimespan
        )
        let firstDay = Object.keys(dailyUsageJourneyVolume)[0];
        let secondDay = Object.keys(dailyUsageJourneyVolume)[1];
        let dailyGrowthRate = dailyUsageJourneyVolume[secondDay]/dailyUsageJourneyVolume[firstDay];
        let expectedValue = (1 + 0.2)**(1/30);
        expect(dailyGrowthRate).toBeCloseTo(expectedValue, 4);
    }
)

test(
    'computeUsageJourneyVolume_check_growth_rate_yearly', () => {
        netGrowRateInPercentage = 30;
        netGrowthRateTimespan = 'year';
        let dailyUsageJourneyVolume = computeUsageJourneyVolume(
            startDate,
            modelingDurationValue,
            modelingDurationUnit,
            netGrowRateInPercentage,
            netGrowthRateTimespan,
            initialUsageJourneyVolume,
            initialUsageJourneyVolumeTimespan
        )
        let firstDay = Object.keys(dailyUsageJourneyVolume)[0];
        let secondDay = Object.keys(dailyUsageJourneyVolume)[1];
        let dailyGrowthRate = dailyUsageJourneyVolume[secondDay]/dailyUsageJourneyVolume[firstDay];
        let expectedValue = (1 + 0.3)**(1/365);
        expect(dailyGrowthRate).toBeCloseTo(expectedValue, 4);
    }
)

test('sumUsageJourneyVolumeByDisplayGranularity_monthly-check_length', () => {
    let displayGranularity = 'month';
    let aggregatedData = sumUsageJourneyVolumeByDisplayGranularity(testDailyUsageJourneyVolume, displayGranularity);
    expect(Object.keys(aggregatedData).length).toBe(12);
})

test('sumUsageJourneyVolumeByDisplayGranularity_yearly-check_length', () => {
    let displayGranularity = 'year';
    let modelingDurationValue = 2;
    let dailyUsageJourneyVolume = computeUsageJourneyVolume(
        startDate,
        modelingDurationValue,
        modelingDurationUnit,
        netGrowRateInPercentage,
        netGrowthRateTimespan,
        initialUsageJourneyVolume,
        initialUsageJourneyVolumeTimespan
    )
    let aggregatedData = sumUsageJourneyVolumeByDisplayGranularity(dailyUsageJourneyVolume, displayGranularity);
    expect(Object.keys(aggregatedData).length).toBe(2);
})
