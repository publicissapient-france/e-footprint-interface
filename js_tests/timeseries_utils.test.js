const {
    convertHourlyEmissionsByHardwareTypeFromStartDateToDailyDict,
    cumulativeSumFromArray,
    getTimeIndexFromDataByHardwareTypeEmissions
} = require('../theme/static/scripts/timeseries_utils.js');
const { DateTime, Duration } = require("luxon");
global.luxon = { DateTime, Duration };
const {join} = require("node:path");
const {readFileSync} = require("node:fs");
const exp = require("node:constants");

test(
    'Check getTimeIndexFromDataByHardwareTypeEmissions return an Array with the right number of elements and check' +
    ' each elements of the list with Month parameter' +
    ' ', () => {
        let startDate = "2025-06-01 00:00:00";
        let granularity = "month";
        let nbValues = 24;

        let csvPath = join(__dirname, "timeseries_files_test/list_month.csv");
        let csvContent = readFileSync(csvPath, "utf8");
        let lines = csvContent.trim().split("\n");
        let expectedData = lines.slice(1);

        let result = getTimeIndexFromDataByHardwareTypeEmissions(startDate, granularity, nbValues);
        expect(result.length).toBe(24);
        expect(result).toEqual(expectedData);
    }
)
test(
    'Check getTimeIndexFromDataByHardwareTypeEmissions return an Array with the right number of elements and check' +
    ' each elements of the list with Year parameter' +
    ' ', () => {
        let startDate = "2025-06-01 00:00:00";
        let granularity = "year";
        let nbValues = 20;

        let csvPath = join(__dirname, "timeseries_files_test/list_year.csv");
        let csvContent = readFileSync(csvPath, "utf8");
        let lines = csvContent.trim().split("\n");
        let expectedData = lines.slice(1);

        let result = getTimeIndexFromDataByHardwareTypeEmissions(startDate, granularity, nbValues)
        expect(result.length).toBe(20);
        expect(result).toEqual(expectedData);
    }
)

test(
    'Check convertHourlyEmissionsByHardwareTypeFromStartDateToDailyDict return an Dict with the right number of' +
    ' elements and check index', () => {
        let hardwareTypes = {
            "hardwareTypeA": {},
            "hardwareTypeB": {},
            "hardwareTypeC": {}
        };
        let emissions = {
            "hardwareTypeA": {
                values: new Array(24 * 7).fill(1),
                start_date: "2025-01-01 00:00:00"
            },
            "hardwareTypeB": {
                values: new Array(24 * 7).fill(2),
                start_date: "2025-01-01 00:00:00"
            },
            "hardwareTypeC": {
                values: new Array(24 * 7).fill(3),
                start_date: "2025-01-01 00:00:00"
            }
        };

        let expected_emissions = {
            "hardwareTypeA": {
                "values": new Array(7).fill(24),
                "index": ["2025-01-01", "2025-01-02", "2025-01-03", "2025-01-04", "2025-01-05", "2025-01-06", "2025-01-07"],
            },
            "hardwareTypeB": {
                "values": new Array(7).fill(48),
                "index": ["2025-01-01", "2025-01-02", "2025-01-03", "2025-01-04", "2025-01-05", "2025-01-06", "2025-01-07"],
            },
            "hardwareTypeC": {
                "values": new Array(7).fill(72),
                "index": ["2025-01-01", "2025-01-02", "2025-01-03", "2025-01-04", "2025-01-05", "2025-01-06", "2025-01-07"],
            }
        };

        let result = convertHourlyEmissionsByHardwareTypeFromStartDateToDailyDict(hardwareTypes, emissions)
        Object.keys(result).forEach((key) => {
            expect(Object.keys(result[key]).length).toBe(7);
            expect(Object.values(result[key])).toEqual(expected_emissions[key].values);
        });
    }
)

test(
    'Check cumulativeSumFromArray return an Dict with the right number of' +
    ' elements and check index', () => {
        const arrayEmissions = [
            744, 672, 744, 720, 744, 720, 744, 744, 720, 744, 720, 744,
            744, 672, 744, 720, 744, 720, 744, 744, 720, 744, 720, 744
        ]
        let expected_emissions = [
            744, 1416, 2160, 2880, 3624, 4344, 5088, 5832, 6552, 7296, 8016, 8760,
            9504, 10176, 10920, 11640, 12384, 13104, 13848, 14592, 15312, 16056, 16776, 17520
        ];
        let result = cumulativeSumFromArray(arrayEmissions);
        expect(expected_emissions).toEqual(result);
    }
)
