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

        cy.visit("/model_builder/");
        cy.get('button[hx-get="/model_builder/open-import-json-panel/"]').click();
        let fileTest = 'cypress/fixtures/efootprint-model-no-job.json'
        cy.get('input[type="file"]').selectFile(fileTest);
        cy.get('button[type="submit"]').click();

        cy.get('button[hx-get^="/model_builder/open_create_job_panel/"][hx-vals*="'+ujsOne.replaceAll(' ', '-')+'"]').click();
        cy.get('#name').type(jobOne);
        cy.get('#service').select(service);
        cy.get('#formPanel form').find('button[type="submit"]').click();

        cy.get('button[hx-get^="/model_builder/open_create_job_panel/"][hx-vals*="'+ujsTwo.replaceAll(' ', '-')+'"]').click();
        cy.get('#formPanel').should('be.visible');
        cy.get('#name').type(jobTwo);
        cy.get('#service').select(service);
        cy.get('#formPanel form').find('button[type="submit"]').click();

        cy.get("button[id^='button-id-'][id$='"+jobOne.replaceAll(' ', '-')+"']").should('exist');
        cy.get('button[hx-get^="/model_builder/open_create_job_panel/"][hx-vals*="'+ujsOne.replaceAll(' ', '-')+'"]').should('exist');

        cy.get('div[id^="flush-id-"][id$="'+ujsOne.replaceAll(' ', '-')+'"]').within(() => {
            cy.get("button[id^='button-id-'][id$='"+jobOne.replaceAll(' ', '-')+"']").then(($firstButton) => {
                cy.get('button[hx-get^="/model_builder/open_create_job_panel/"][hx-vals*="'+ujsOne.replaceAll(' ', '-')+'"]').then(($secondButton) => {
                    const firstTop = $firstButton[0].getBoundingClientRect().top;
                    const secondTop = $secondButton[0].getBoundingClientRect().top;
                    expect(secondTop).to.be.greaterThan(firstTop);
                });
            });
        });


    });
});
