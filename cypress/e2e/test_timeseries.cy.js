describe('Tests dedicated to the timeseries generation', () => {
    it('Check if we can open several times the form about usage patten and chart is always displayed', () => {

        let ujName = "Test E2E UJ";
        let upNameOne = "Test E2E Usage Pattern 1";
        let upNameTwo = "Test E2E Usage Pattern 2";

        cy.visit("/");
        cy.get('#btn-start-modeling-my-service').click();
        cy.get('#model-canva').should('be.visible');
        cy.window().its('LeaderLine')

        cy.get('#btn-add-usage-journey').click();
        cy.get('#btn-add-usage-journey').should('be.visible');
        cy.get('#name').type(ujName);
        cy.get('#btn-submit-form').click();
        cy.get('#form-add-usage-journey').should('not.exist');
        cy.get('div[id$="'+ujName.replaceAll(' ', '-')+'"]').should('have.class', 'leader-line-object')

        cy.get('button').contains('Add usage pattern').click();
        cy.get('#sidePanel').should('be.visible');
        cy.get('#timeSeriesChart').then(($canvas) =>{
            let canvas = $canvas[0]
            let ctx = canvas.getContext('2d');
            expect(ctx).not.to.be.null;
        });
        cy.get('#name').type(upNameOne);

        cy.get('#start_date').click();
        cy.get('input[class="numInput cur-year"]').type('2026');
        cy.get('span[aria-label="January 1, 2026"]').click()
        cy.get('#modeling_duration_value').click();
        cy.get('#modeling_duration_value').invoke('val', '2').trigger('change');
        cy.get('#net_growth_rate_in_percentage').click();
        cy.get('#net_growth_rate_in_percentage').invoke('val', '25').trigger('change');
        cy.get('#net_growth_rate_timespan').select('year');
        cy.get('#btn-submit-form').click();



        cy.get('button').contains('Add usage pattern').click();
        cy.get('#sidePanel').should('be.visible');
        cy.get('#timeSeriesChart').then(($canvas) =>{
            let canvas = $canvas[0]
            let ctx = canvas.getContext('2d');
            expect(ctx).not.to.be.null;
        });
        cy.get('#name').type(upNameTwo);
        cy.get('#start_date').click();
        cy.get('input[class="numInput cur-year"]').type('2027');
        cy.get('span[aria-label="January 1, 2027"]').click()
        cy.get('#modeling_duration_value').click();
        cy.get('#modeling_duration_value').invoke('val', '5').trigger('change');
        cy.get('#net_growth_rate_in_percentage').click();
        cy.get('#net_growth_rate_in_percentage').invoke('val', '15').trigger('change');
        cy.get('#net_growth_rate_timespan').select('month');

        cy.get('#btn-submit-form').click();
        cy.get('#sidePanel').should('not.contain.html');
        cy.wait(500)
        cy.get('button[id^="button-id-"][id$="'+upNameOne.replaceAll(' ', '-')+'"]').should('be.visible').click();
        cy.get('#timeSeriesChart').then(($canvas) =>{
            let canvas = $canvas[0]
            let ctx = canvas.getContext('2d');
            expect(ctx).not.to.be.null;
        });
    });

    it('Test the timeseries generation and check if the result has the right number of elements', () => {

        let ujName = "Test E2E UJ";
        let upNameOne = "Test E2E Usage Pattern 1";
        let intValue = null

        cy.visit("/");
        cy.get('#btn-start-modeling-my-service').click();
        cy.get('#model-canva').should('be.visible');
        cy.window().its('LeaderLine')

        cy.get('#btn-add-usage-journey').click();
        cy.get('#btn-add-usage-journey').should('be.visible');
        cy.get('#name').type(ujName);
        cy.get('#btn-submit-form').click();
        cy.get('#form-add-usage-journey').should('not.exist');
        cy.get('div[id$="'+ujName.replaceAll(' ', '-')+'"]').should('have.class', 'leader-line-object')

        cy.get('button').contains('Add usage pattern').click();
        cy.get('#sidePanel').should('be.visible');
        cy.get('#name').type(upNameOne);

        cy.get('#start_date').click();
        cy.get('span[aria-label="January 1, 2025"]').click();
        cy.get('#modeling_duration_value').click();

        cy.get('#modeling_duration_value').invoke('val', '2').trigger('input');
        cy.get('#modeling_duration_value_error_message').should('not.contain.html');


        cy.get('#modeling_duration_value').invoke('val', '15').trigger('input');
        cy.get('#modeling_duration_value').invoke('attr', 'max').then((maxValue) => {
            cy.get('#modeling_duration_value')
            .invoke('val')
            .then((val) => {
                intValue = parseInt(val, 10);
                cy.wrap(intValue).should('be.lte', Number(maxValue));
            });
            cy.get('#modeling_duration_value_error_message').should(
                'contain.text', `Modeling duration value must be less than or equal to ${maxValue}`);
        });

        cy.get('#modeling_duration_value').invoke('val', '0').trigger('input');
        cy.get('#modeling_duration_value').invoke('attr', 'max').then((maxValue) => {
            cy.get('#modeling_duration_value')
            .invoke('val')
            .then((val) => {
                intValue = parseInt(val, 10);
                cy.wrap(intValue).should('eq', 1);
            });
            cy.get('#modeling_duration_value_error_message').should(
                'contain.text', `Modeling duration value must be greater than 0 and can't be empty`);
        });

        cy.get('#modeling_duration_unit').select('month');

        cy.get('#modeling_duration_value').invoke('val', '12').trigger('input');
        cy.get('#modeling_duration_value_error_message').should('not.contain.html');

        cy.get('#modeling_duration_value').invoke('val', '150').trigger('input');
        cy.get('#modeling_duration_value').invoke('attr', 'max').then((maxValue) => {
            cy.get('#modeling_duration_value')
            .invoke('val')
            .then((val) => {
                intValue = parseInt(val, 10);
                cy.wrap(intValue).should('be.lte', Number(maxValue));
            });
            cy.get('#modeling_duration_value_error_message').should(
                'contain.text', `Modeling duration value must be less than or equal to ${maxValue}`);
        });

        cy.get('#modeling_duration_value').invoke('val', '0').trigger('input');
        cy.get('#modeling_duration_value').invoke('attr', 'max').then((maxValue) => {
            cy.get('#modeling_duration_value')
            .invoke('val')
            .then((val) => {
                intValue = parseInt(val, 10);
                cy.wrap(intValue).should('eq', 12);
            });
            cy.get('#modeling_duration_value_error_message').should(
                'contain.text', `Modeling duration value must be greater than 0 and can't be empty`);
        });

        cy.get('#modeling_duration_value').invoke('val', '24').trigger('input');
        cy.get('#modeling_duration_value').invoke('val', '12').trigger('input');
        cy.get('#modeling_duration_value_error_message').should('not.contain.html');
    });
});
