describe('Test de la page d\'accueil', () => {
    it('Ouvre la page d\'accueil et interagit avec un bouton', () => {

        let ujName = "Test E2E UJ";
        let ujName2 = "Test E2E UJ 2";
        let ujsOne = "Test E2E UJS 1";
        let ujsTwo = "Test E2E UJS 2";
        let server = "Test E2E Server";
        let service = "Test E2E Service";
        let jobOne = "Test E2E Job 1";
        let jobTwo = "Test E2E Job 2";
        let upName = "Test E2E Usage Pattern";

        cy.visit("/");
        cy.get('#btn-start-modeling-my-service').click();
        cy.get('#model-canva').should('be.visible');
        cy.window().its('LeaderLine')

        // Create UJ one and two
        cy.get('#btn-add-usage-journey').click();
        cy.get('#btn-add-usage-journey').should('be.visible');
        cy.get('#btn-submit-form-add-usage-journey').click();
        cy.get('#name').then(($input) => {
        expect($input[0].validationMessage).to.not.be.empty;
        });
        cy.get('#name').type(ujName);
        cy.get('#btn-submit-form-add-usage-journey').click();
        cy.get('#form-add-usage-journey').should('not.exist');

        cy.get('#btn-add-usage-journey').click();
        cy.get('#name').type(ujName2);
        cy.get('#btn-submit-form-add-usage-journey').click();
        cy.get('#form-add-usage-journey').should('not.exist');

        // User journeys must be visible then add user journey steps to UJ 1
        cy.get('div[id$="'+ujName.replaceAll(' ', '-')+'"]').should('have.class', 'leader-line-object')
        cy.get('div[id$="'+ujName2.replaceAll(' ', '-')+'"]').should('have.class', 'leader-line-object')
        cy.get('div[id$="'+ujName.replaceAll(' ', '-')+'"]')
          .contains('button', 'Add usage journey step')
          .click();
        cy.get('#formPanel').contains('form', 'Add new usage journey step').should('be.visible');
        cy.get('#name').type(ujsOne);
        cy.get('#user_time_spent').type('10.1');
        cy.get('#formPanel form').find('button[type="submit"]').click();
        cy.get('#formPanel').should('exist').find('form').should('not.exist');
        // @ts-ignore
        cy.get('div[id$="'+ujName.replaceAll(' ', '-')+'"]').should('have.class', 'leader-line-object')
        cy.get('div[id$="'+ujName.replaceAll(' ', '-')+'"]')
          .contains('button', 'Add usage journey step')
          .click();
        cy.get('#formPanel').contains('form', 'Add new usage journey step').should('be.visible');
        cy.get('#name').type(ujsTwo);
        cy.get('#user_time_spent').type('20,2');
        cy.get('#formPanel form').find('button[type="submit"]').click();
        cy.get('#formPanel').should('exist').find('form').should('not.exist');
        cy.get('div[id$="'+ujName.replaceAll(' ', '-')+'"]').should('have.class', 'leader-line-object')
        //on vérifie que les deux ujs ont bien été ajoutés
        cy.get('div[id*="'+ujName.replaceAll(' ', '-')+'"]').find('div[id*="'+ujsOne.replaceAll(' ', '-')+'"]').should('exist');
        cy.get('div[id*="'+ujName.replaceAll(' ', '-')+'"]').find('div[id*="'+ujsTwo.replaceAll(' ', '-')+'"]').should('exist');

        // Add server
        cy.get('#btn-add-server').click();
        cy.get('#formPanel').contains('form', 'Add new server').should('be.visible');
        cy.get('#name').type(server);
        cy.get('#type_object_available').select('BoaviztaCloudServer');
        cy.get('#instance_type').type('c4.8xlarge');
        cy.get('#formPanel form').find('button[type="submit"]').click();

        cy.get('div[id$="'+server.replaceAll(' ', '-')+'"]').should('have.class', 'list-group-item')
        // get the button inside with attribute data-bs-target begin with '#flush-id' and ended with '-Test-E2E-Server'
        cy.get('button[data-bs-target^="#flush-"][data-bs-target$="'+server.replaceAll(' ', '-')+'"]').click();
        // get the button with attribute hx-get begin with '/model_builder/open-create-service-panel/' and ended with 'Test-E2E-Server'
        cy.get('button[hx-get^="/model_builder/open-create-service-panel"][hx-get$="'+server.replaceAll(' ', '-')+'/"]').click();
        cy.get('#name').type(service);
        cy.get('#technology').select('php-symfony');
        cy.get('#formPanel form').find('button[type="submit"]').click();
        cy.get('button[hx-get^="/model_builder/open-edit-object-panel/"][hx-get$="'+service.replaceAll(' ', '-')+'/"]').should('be.visible');

        // Add jobs
        cy.get('button[data-bs-target^="#flush-"][data-bs-target$="'+ujsOne.replaceAll(' ', '-')+'"]').click();
        cy.get('button[hx-get^="/model_builder/open_create_job_panel/"][hx-vals*="'+ujsOne.replaceAll(' ', '-')+'"]').click();
        cy.get('#name').type(jobOne);
        cy.get('#service').select(service);
        cy.get('#formPanel form').find('button[type="submit"]').click();
        cy.get('button[hx-get^="/model_builder/open-edit-object-panel/"][hx-get$="'+jobOne.replaceAll(' ', '-')+'/"]').should('be.visible');

        cy.get('button[data-bs-target^="#flush-"][data-bs-target$="'+ujsTwo.replaceAll(' ', '-')+'"]').click();
        cy.get('button[hx-get^="/model_builder/open_create_job_panel/"][hx-vals*="'+ujsTwo.replaceAll(' ', '-')+'"]').click();
        cy.get('#formPanel').should('be.visible');
        cy.get('#name').type(jobTwo);
        cy.get('#service').select(service);
        cy.get('#formPanel form').find('button[type="submit"]').click();
        cy.get('button[hx-get^="/model_builder/open-edit-object-panel/"][hx-get$="'+jobTwo.replaceAll(' ', '-')+'/"]').should('be.visible');

        // Add usagePattern
        cy.get('button').contains('Add usage pattern').click();
        cy.get('#formPanel').should('be.visible');
        cy.get('#name').type(upName);

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

        cy.get('button[data-bs-target="#usage-pattern-attributes-modal-timeseries"]').click();
        cy.get('#usage-pattern-attributes-modal-timeseries').should('be.visible');
        cy.get('#timeframe_start_date').click();
        // Replace the date by 2026-01-01 in timeframe_start_date
        cy.get('#timeframe_start_date').invoke('val', '2026-01-02').trigger('change');
        cy.get('#timeframe_value').invoke('val', '2').trigger('change');
        cy.get('#net_growth_rate_value').invoke('val', '25').trigger('change');
        cy.get('#net_growth_rate_range').select('year');
        cy.wait(1000);
        cy.get('button[onclick^="checkAttributes(\'timeseries\')"]').click();
        cy.get('#usage-pattern-attributes-modal-timeseries').should('not.exist');

        cy.get('#save_usage_pattern_btn').click();
        cy.get('#formPanel').should('not.contain.html');
        cy.get('button[id^="button-id-"][id$="'+upName.replaceAll(' ', '-')+'"]').should('be.visible');

        cy.get('button[id^="button-id-"][id$="Test-E2E-UJ-2"]').click();
        cy.wait(500);
        cy.get('#btn-ask-delete').should('be.enabled').click();
        cy.get('button').contains('Yes, delete').should('be.enabled').click();
        cy.get("#model-builder-modal").should("not.exist");
        cy.get('button[id^="button-id-"][id$="Test-E2E-UJ-2"]').should('not.exist');

        cy.get('button[hx-get="/model_builder/result-chart/"]').click();
        cy.get('#resultModal').should('be.visible');
    });
});
