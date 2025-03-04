describe('Test de la page d\'accueil', () => {
    it('Ouvre la page d\'accueil et interagit avec un bouton', () => {

        let ujName = "Test E2E UJ";

        let upNameOne = "Test E2E Usage Pattern 1";

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
        cy.get('#name').type(upNameOne);

        cy.get('button[data-bs-target="#usage-pattern-attributes-modal-timeseries"]').click();
        cy.get('#usage-pattern-attributes-modal-timeseries').should('be.visible');

        cy.get('#usage-pattern-attributes-modal-timeseries input[name="start_date"]').click();
        cy.get('#usage-pattern-attributes-modal-timeseries input[name="start_date"]').invoke('val', '2026-01-02').trigger('change');
        cy.get('#usage-pattern-attributes-modal-timeseries input[name="modeling_duration_value"]').click();
        cy.get('#usage-pattern-attributes-modal-timeseries input[name="modeling_duration_value"]').invoke('val', '2').trigger('change');
        cy.get('#usage-pattern-attributes-modal-timeseries input[name="net_growth_rate_in_percentage"]').click();
        cy.get('#usage-pattern-attributes-modal-timeseries input[name="net_growth_rate_in_percentage"]').invoke('val', '25').trigger('change');
        cy.get('#usage-pattern-attributes-modal-timeseries select[name="net_growth_rate_timespan"]').select('year');
        cy.get('#save_time_series_btn').click();
        cy.get('#usage-pattern-attributes-modal-timeseries').should('not.be.visible');
        cy.wait(1000)

        cy.get('button[data-bs-target="#usage-pattern-attributes-modal-timeseries"]').click();
        cy.get('#usage-pattern-attributes-modal-timeseries').should('be.visible');

        cy.get('#usage-pattern-attributes-modal-timeseries input[name="start_date"]').click();
        cy.get('#usage-pattern-attributes-modal-timeseries input[name="start_date"]').invoke('val', '2027-01-02').trigger('change');
        cy.get('#usage-pattern-attributes-modal-timeseries input[name="modeling_duration_value"]').click();
        cy.get('#usage-pattern-attributes-modal-timeseries input[name="modeling_duration_value"]').invoke('val', '5').trigger('change');
        cy.get('#usage-pattern-attributes-modal-timeseries input[name="net_growth_rate_in_percentage"]').click();
        cy.get('#usage-pattern-attributes-modal-timeseries input[name="net_growth_rate_in_percentage"]').invoke('val', '15').trigger('change');
        cy.get('#usage-pattern-attributes-modal-timeseries select[name="net_growth_rate_timespan"]').select('month');
        cy.get('#save_time_series_btn').click();
        cy.get('#usage-pattern-attributes-modal-timeseries').should('not.be.visible');
        cy.wait(1000)

        cy.get('#save_usage_pattern_btn').click();
        cy.get('#formPanel').should('not.contain.html');
        cy.get('button[id^="button-id-"][id$="'+upNameOne.replaceAll(' ', '-')+'"]').should('be.visible');

    });
});
