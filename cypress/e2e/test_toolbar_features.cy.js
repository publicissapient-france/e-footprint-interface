describe("Test - Toolbars import/export/reboot", () => {
    it("Import one JSON file when the model is empty and check that objects has been adde", () => {
        let ujName = "Test E2E UJ";
        let ujsOne = "Test E2E UJ 1";
        let ujsTwo = "Test E2E UJ 2";
        let server = "Test E2E Server";
        let service = "Test E2E Service";
        let jobOne = "Test E2E Job 1";
        let jobTwo = "Test E2E Job 2";
        let upName = "Test E2E Usage Pattern";

        cy.visit("/");
        cy.get('#btn-start-modeling-my-service').click();
        cy.get('#model-canva').should('be.visible');
        cy.get('button[hx-get="/model_builder/open-import-json-panel/"]').click();
        let fileTest = 'cypress/fixtures/efootprint-model-system-data.json'
        cy.get('input[type="file"]').selectFile(fileTest);
        cy.get('input[type="file"]').then(($input) => {
          expect($input[0].files.length).to.equal(1);
          expect($input[0].files[0].name).to.equal('efootprint-model-system-data.json');
        });
        cy.get('button[type="submit"]').click();

        cy.get('button[id^="button-id-"][id$="'+upName.replaceAll(' ', '-')+'"]').should('exist').should('be.visible');
        cy.get('button[id^="button-id-"][id$="'+ujName.replaceAll(' ', '-')+'"]').should('exist').should('be.visible');
        cy.get('button[id^="button-id-"][id$="'+server.replaceAll(' ', '-')+'"]').should('exist').should('be.visible');
        cy.get('button[id^="button-id-"][id$="'+ujsOne.replaceAll(' ', '-')+'"]').should('exist').should('be.visible');
        cy.get('button[id^="button-id-"][id$="'+ujsTwo.replaceAll(' ', '-')+'"]').should('exist').should('be.visible');
        cy.get('button[id^="button-id-"][id$="'+jobOne.replaceAll(' ', '-')+'"]').should('exist').should('not.be.visible');
        cy.get('button[id^="button-id-"][id$="'+jobTwo.replaceAll(' ', '-')+'"]').should('exist').should('not.be.visible');
        cy.get('button[id^="button-id-"][id$="'+service.replaceAll(' ', '-')+'"]').should('exist').should('not.be.visible');
    });

    it("Import a new JSON file when the model already contained objets to check previous objects are removed and" +
        "  new objets has been added", () => {
        let ujName = "Test E2E UJ";
        let ujsOne = "Test E2E UJ 1";
        let ujsTwo = "Test E2E UJ 2";
        let server = "Test E2E Server";
        let service = "Test E2E Service";
        let jobOne = "Test E2E Job 1";
        let jobTwo = "Test E2E Job 2";
        let upName = "Test E2E Usage Pattern";

        cy.visit("/");
        cy.get('#btn-start-modeling-my-service').click();
        cy.get('#model-canva').should('be.visible');
        cy.get('button[hx-get="/model_builder/open-import-json-panel/"]').click();
        let fileTest = 'cypress/fixtures/efootprint-model-system-data.json'
        cy.get('input[type="file"]').selectFile(fileTest);
        cy.get('input[type="file"]').then(($input) => {
          expect($input[0].files.length).to.equal(1);
          expect($input[0].files[0].name).to.equal('efootprint-model-system-data.json');
        });
        cy.get('button[type="submit"]').click();

        cy.get('button[id^="button-id-"][id$="'+upName.replaceAll(' ', '-')+'"]').should('exist').should('be.visible');
        cy.get('button[id^="button-id-"][id$="'+ujName.replaceAll(' ', '-')+'"]').should('exist').should('be.visible');
        cy.get('button[id^="button-id-"][id$="'+server.replaceAll(' ', '-')+'"]').should('exist').should('be.visible');
        cy.get('button[id^="button-id-"][id$="'+ujsOne.replaceAll(' ', '-')+'"]').should('exist').should('be.visible');
        cy.get('button[id^="button-id-"][id$="'+ujsTwo.replaceAll(' ', '-')+'"]').should('exist').should('be.visible');
        cy.get('button[id^="button-id-"][id$="'+jobOne.replaceAll(' ', '-')+'"]').should('exist').should('not.be.visible');
        cy.get('button[id^="button-id-"][id$="'+jobTwo.replaceAll(' ', '-')+'"]').should('exist').should('not.be.visible');
        cy.get('button[id^="button-id-"][id$="'+service.replaceAll(' ', '-')+'"]').should('exist').should('not.be.visible');

        cy.get('button[hx-get="/model_builder/open-import-json-panel/"]').click();
        cy.get('input[type="file"]').selectFile(fileTest);
        cy.get('input[type="file"]').then(($input) => {
          expect($input[0].files.length).to.equal(1);
          expect($input[0].files[0].name).to.equal('efootprint-model-system-data.json');
        });

        cy.window().then((win) => {
          cy.spy(win, 'initLeaderLines').as('initLeaderLines');
        });
        cy.get('button[type="submit"]').click();
        cy.get('@initLeaderLines').should('have.been.called');

        cy.get('button[id^="button-id-"][id$="'+upName.replaceAll(' ', '-')+'"]').should('exist').should('be.visible');
        cy.get('button[id^="button-id-"][id$="'+ujName.replaceAll(' ', '-')+'"]').should('exist').should('be.visible');
        cy.get('button[id^="button-id-"][id$="'+server.replaceAll(' ', '-')+'"]').should('exist').should('be.visible');
        cy.get('button[id^="button-id-"][id$="'+ujsOne.replaceAll(' ', '-')+'"]').should('exist').should('be.visible');
        cy.get('button[id^="button-id-"][id$="'+ujsTwo.replaceAll(' ', '-')+'"]').should('exist').should('be.visible');
        cy.get('button[id^="button-id-"][id$="'+jobOne.replaceAll(' ', '-')+'"]').should('exist').should('not.be.visible');
        cy.get('button[id^="button-id-"][id$="'+jobTwo.replaceAll(' ', '-')+'"]').should('exist').should('not.be.visible');
        cy.get('button[id^="button-id-"][id$="'+service.replaceAll(' ', '-')+'"]').should('exist').should('not.be.visible');
    });

    it("check if we reset the model all objets and leaderlines have been removed", () => {
        let ujName = "Test E2E UJ";
        let ujsOne = "Test E2E UJ 1";
        let ujsTwo = "Test E2E UJ 2";
        let server = "Test E2E Server";
        let service = "Test E2E Service";
        let jobOne = "Test E2E Job 1";
        let jobTwo = "Test E2E Job 2";
        let upName = "Test E2E Usage Pattern";

        cy.visit("/");
        cy.get('#btn-start-modeling-my-service').click();
        cy.get('button[hx-get="/model_builder/open-import-json-panel/"]').click();
        let fileTest = 'cypress/fixtures/efootprint-model-system-data.json'
        cy.get('input[type="file"]').selectFile(fileTest);
        cy.get('button[type="submit"]').click();

        cy.wait(1000);

        cy.get('a[id="btn-reboot-modeling"]').click();

        cy.get('button[id^="button-id-"][id$="'+upName.replaceAll(' ', '-')+'"]').should('not.exist');
        cy.get('button[id^="button-id-"][id$="'+ujName.replaceAll(' ', '-')+'"]').should('not.exist');
        cy.get('button[id^="button-id-"][id$="'+server.replaceAll(' ', '-')+'"]').should('not.exist');
        cy.get('button[id^="button-id-"][id$="'+ujsOne.replaceAll(' ', '-')+'"]').should('not.exist');
        cy.get('button[id^="button-id-"][id$="'+ujsTwo.replaceAll(' ', '-')+'"]').should('not.exist');
        cy.get('button[id^="button-id-"][id$="'+jobOne.replaceAll(' ', '-')+'"]').should('not.exist');
        cy.get('button[id^="button-id-"][id$="'+jobTwo.replaceAll(' ', '-')+'"]').should('not.exist');
        cy.get('button[id^="id-"][id$="'+service.replaceAll(' ', '-')+'"]').should('not.exist');

        //any svg with class leader-line should not exist
        cy.get('svg[class="leader-line"]').should('not.exist');
    });
});
