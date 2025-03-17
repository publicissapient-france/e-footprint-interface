import "cypress-real-events";
describe("Test - Result panel", () => {
    it("Check if the model cannot be calculated if the modal exception is displayed and the result panel not showed", () => {
        let ujName = "Test E2E UJ";
        let ujsOne = "Test E2E UJ 1";
        let ujsTwo = "Test E2E UJ 2";
        let server = "Test E2E Server";
        let service = "Test E2E Service";
        let jobOne = "Test E2E Job 1";
        let jobTwo = "Test E2E Job 2";
        let upName = "Test E2E Usage Pattern";

        cy.visit("/model_builder/");
        cy.get('button[hx-get="/model_builder/open-import-json-panel/"]').click();
        let fileTest = 'cypress/fixtures/efootprint-model-no-job.json'
        cy.get('input[type="file"]').selectFile(fileTest);
        cy.get('button[type="submit"]').click();

        cy.get('#btn-open-panel-result')
        .realTouch('start', { x: 100, y: 300 })
        .realTouch('move', { x: 100, y: 200 })
        .realTouch('end', { x: 100, y: 200 });

        cy.get('#panel-result-btn').should('not.have.css', 'height', '93vh');
        cy.get('button').contains('Go back').should('be.exist');
    });

    it("Check that when the model can be calculated the panel is displayed and can be swiped down", () => {
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
        cy.wait(1000);
        cy.get('button[id^="button-id-"][id$="'+upName.replaceAll(' ', '-')+'"]').should('exist').should('be.visible');

        cy.get('#btn-open-panel-result')
        .realTouch('start', { x: 100, y: 300 })
        .realTouch('move', { x: 100, y: 200 })
        .realTouch('end', { x: 100, y: 200 });
        cy.wait(2000);
        cy.get('#inner-panel-result').should('be.visible').find('div[onclick="hidePanelResult()"]')
        .realTouch('start', { x: 100, y: 300 })
        .realTouch('move', { x: 100, y: 400 })
        .realTouch('end', { x: 100, y: 400 });
    });
});
