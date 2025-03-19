const {
    convertHourlyToDailyEmissionsByHardwareType,
} = require('../theme/static/scripts/result_charts.js');
const { DateTime, Duration } = require("luxon");
global.luxon = { DateTime, Duration };
const exp = require("node:constants");

test(
    'Check convertHourlyToDailyEmissionsByHardwareType return an Dict with the right number of' +
    ' elements and check index', () => {
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

        let result = convertHourlyToDailyEmissionsByHardwareType(emissions)
        Object.keys(result).forEach((key) => {
            expect(Object.keys(result[key]).length).toBe(7);
            expect(Object.values(result[key])).toEqual(expected_emissions[key].values);
        });
    }
)
