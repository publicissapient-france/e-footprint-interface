describe('Test de la page d\'accueil', () => {
    it('Ouvre la page d\'accueil et interagit avec un bouton', () => {

        let ujName = "Test E2E UJ";
        let upNameOne = "Test E2E Usage Pattern 1";
        let intValue = null

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

        cy.get('#start_date').click();
        cy.get('#modeling_duration_value').click();

        cy.get('#modeling_duration_value').invoke('val', '2').trigger('change');
        cy.get('#modeling_duration_value_error_message').should('not.contain.html');


        cy.get('#modeling_duration_value').invoke('val', '15').trigger('change');
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

        cy.get('#modeling_duration_value').invoke('val', '0').trigger('change');
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

        cy.get('#modeling_duration_value').invoke('val', '12').trigger('change');
        cy.get('#modeling_duration_value_error_message').should('not.contain.html');

        cy.get('#modeling_duration_value').invoke('val', '150').trigger('change');
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

        cy.get('#modeling_duration_value').invoke('val', '0').trigger('change');
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

        cy.get('#modeling_duration_value').invoke('val', '24').trigger('change');
        cy.get('#modeling_duration_value').invoke('val', '12').trigger('change');
        cy.get('#modeling_duration_value_error_message').should('not.contain.html');
    });
});
