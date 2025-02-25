describe("Test - Import JSON", () => {
    it("Pick one JSON file and check transfert status", () => {
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
          cy.spy(win, 'removeAllLines').as('removeAllLines');
        });
        cy.get('button[type="submit"]').click();
        cy.get('@removeAllLines').should('have.been.called');

        cy.get('button[id^="button-id-"][id$="'+upName.replaceAll(' ', '-')+'"]').should('exist').should('be.visible');
        cy.get('button[id^="button-id-"][id$="'+ujName.replaceAll(' ', '-')+'"]').should('exist').should('be.visible');
        cy.get('button[id^="button-id-"][id$="'+server.replaceAll(' ', '-')+'"]').should('exist').should('be.visible');
        cy.get('button[id^="button-id-"][id$="'+ujsOne.replaceAll(' ', '-')+'"]').should('exist').should('be.visible');
        cy.get('button[id^="button-id-"][id$="'+ujsTwo.replaceAll(' ', '-')+'"]').should('exist').should('be.visible');
        cy.get('button[id^="button-id-"][id$="'+jobOne.replaceAll(' ', '-')+'"]').should('exist').should('not.be.visible');
        cy.get('button[id^="button-id-"][id$="'+jobTwo.replaceAll(' ', '-')+'"]').should('exist').should('not.be.visible');
        cy.get('button[id^="button-id-"][id$="'+service.replaceAll(' ', '-')+'"]').should('exist').should('not.be.visible');
    });
});
