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
        cy.get('#modal_timeframe_start_date').click();
        cy.get('#modal_timeframe_start_date').invoke('val', '2026-01-02').trigger('change');
        cy.get('#modal_timeframe_value').invoke('val', '2').trigger('change');
        cy.get('#modal_net_growth_rate_value').invoke('val', '25').trigger('change');
        cy.get('#modal_net_growth_rate_period').select('year');
        cy.wait(1000);
        cy.get('button[onclick^="checkAttributes(\'timeseries\')"]').click();
        cy.get('#usage-pattern-attributes-modal-timeseries').should('not.be.visible');

        cy.get('button[data-bs-target="#usage-pattern-attributes-modal-timeseries"]').click();
        cy.get('#usage-pattern-attributes-modal-timeseries').should('be.visible');
        cy.get('#modal_timeframe_start_date').click();
        cy.get('#modal_timeframe_start_date').invoke('val', '2027-01-02').trigger('change');
        cy.get('#modal_timeframe_value').invoke('val', '5').trigger('change');
        cy.get('#modal_net_growth_rate_value').invoke('val', '10').trigger('change');
        cy.get('#modal_net_growth_rate_period').select('year');
        cy.wait(1000);
        cy.get('button[onclick^="checkAttributes(\'timeseries\')"]').click();
        cy.get('#usage-pattern-attributes-modal-timeseries').should('not.be.visible');

        cy.get('button[onclick^="openModalUsagePattern(\'devices\')"]').click();
        cy.get('#usage-pattern-attributes-modal-devices').should('be.visible');
        cy.get('#form-select-devices option')
            .filter((index, option) => option.value.includes('smartphone'))
            .then(option => {
                cy.get('#form-select-devices').select(option.val());
            });
        cy.get('#save-devices-attributes-btn').click();
        cy.get('#usage-pattern-attributes-modal-devices').should('not.exist');

        cy.get('button[onclick^="openModalUsagePattern(\'network\')"]').click();
        cy.get('#usage-pattern-attributes-modal-network').should('be.visible');
        cy.get('#save-network-attributes-btn').click();
        cy.get('#usage-pattern-attributes-modal-network').should('not.exist');

        cy.get('button[onclick^="openModalUsagePattern(\'country\')"]').click();
        cy.get('#usage-pattern-attributes-modal-country').should('be.visible');
        cy.get('#save-country-attributes-btn').click();
        cy.get('#usage-pattern-attributes-modal-country').should('not.exist');

        cy.get('button[onclick^="openModalUsagePattern(\'usage-journey\')"]').click();
        cy.get('#usage-pattern-attributes-modal-usage-journey').should('be.visible');
        cy.get('#save-usage-journey-attributes-btn').click();
        cy.get('#usage-pattern-attributes-modal-usage-journey').should('not.exist');

        cy.get('#save_usage_pattern_btn').click();
        cy.get('#formPanel').should('not.contain.html');
        cy.get('button[id^="button-id-"][id$="'+upNameOne.replaceAll(' ', '-')+'"]').should('be.visible');


    });
});
