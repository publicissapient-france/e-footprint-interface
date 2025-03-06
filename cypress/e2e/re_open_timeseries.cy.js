describe('Test de la page d\'accueil', () => {
    it('Ouvre la page d\'accueil et interagit avec un bouton', () => {

        let ujName = "Test E2E UJ";

        let upNameOne = "Test E2E Usage Pattern 1";
        let upNameTwo = "Test E2E Usage Pattern 2";

        cy.visit("/");
        cy.get('#btn-start-modeling-my-service').click();
        cy.get('#model-canva').should('be.visible');
        cy.window().its('LeaderLine')

        cy.get('#btn-add-usage-journey').click();
        cy.get('#btn-add-usage-journey').should('be.visible');
        cy.get('#btn-submit-form-add-usage-journey').click();
        cy.get('#name').then(($input) => {
            expect($input[0].validationMessage).to.not.be.empty;
        });
        cy.get('#name').type(ujName);
        cy.get('#btn-submit-form-add-usage-journey').click();
        cy.get('#form-add-usage-journey').should('not.exist');
        cy.get('div[id$="'+ujName.replaceAll(' ', '-')+'"]').should('have.class', 'leader-line-object')

        cy.get('button').contains('Add usage pattern').click();
        cy.get('#formPanel').should('be.visible');
        cy.get('#timeSeriesChart').then(($canvas) =>{
            let canvas = $canvas[0]
            let ctx = canvas.getContext('2d');
            expect(ctx).not.to.be.null;
        });
        cy.get('#name').type(upNameOne);

        cy.get('#start_date').click();
        cy.get('#start_date').invoke('val', '2026-01-02').trigger('change');
        cy.get('#modeling_duration_value').click();
        cy.get('#modeling_duration_value').invoke('val', '2').trigger('change');
        cy.get('#net_growth_rate_in_percentage').click();
        cy.get('#net_growth_rate_in_percentage').invoke('val', '25').trigger('change');
        cy.get('#net_growth_rate_timespan').select('year');
        cy.get('#save_usage_pattern_btn').click();



        cy.get('button').contains('Add usage pattern').click();
        cy.get('#formPanel').should('be.visible');
        cy.get('#timeSeriesChart').then(($canvas) =>{
            let canvas = $canvas[0]
            let ctx = canvas.getContext('2d');
            expect(ctx).not.to.be.null;
        });
        cy.get('#name').type(upNameTwo);
        cy.get('#start_date').click();
        cy.get('#start_date').invoke('val', '2027-01-02').trigger('change');
        cy.get('#modeling_duration_value').click();
        cy.get('#modeling_duration_value').invoke('val', '5').trigger('change');
        cy.get('#net_growth_rate_in_percentage').click();
        cy.get('#net_growth_rate_in_percentage').invoke('val', '15').trigger('change');
        cy.get('#net_growth_rate_timespan').select('month');

        cy.get('#save_usage_pattern_btn').click();
        cy.get('#formPanel').should('not.contain.html');
        cy.wait(500)
        cy.get('button[id^="button-id-"][id$="'+upNameOne.replaceAll(' ', '-')+'"]').should('be.visible').click();
        cy.get('#timeSeriesChart').then(($canvas) =>{
            let canvas = $canvas[0]
            let ctx = canvas.getContext('2d');
            expect(ctx).not.to.be.null;
        });
    });
});
