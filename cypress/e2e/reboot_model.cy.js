describe("Test - Import JSON", () => {
    it("Pick one JSON file and check trasnfert status", () => {
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
