describe('Test de la page d\'accueil', () => {
    it('Ouvre la page d\'accueil et interagit avec un bouton', () => {
        let server = "Test E2E Server";
        let service = "Test E2E Service";

        cy.visit("/");
        cy.get('#btn-start-modeling-my-service').click();
        cy.get('#model-canva').should('be.visible');


        //ajout d'un server
        cy.get('#btn-add-server').click();
        cy.get('#sidePanel').contains('div', 'Add new server').should('be.visible');
        cy.get('#name').type(server);
        cy.get('#type_object_available').select('GPUServer');
        cy.get('#sidePanel form').find('button[type="submit"]').click();

        cy.get('div[id$="'+server.replaceAll(' ', '-')+'"]').should('have.class', 'list-group-item')
        cy.get('button[data-bs-target^="#flush-"][data-bs-target$="'+server.replaceAll(' ', '-')+'"]').click();
        cy.get('button[hx-get^="/model_builder/open-create-service-panel"][hx-get$="'+server.replaceAll(' ', '-')+'/"]').click();
        cy.get('#name').type(service);
        cy.get('#provider').select('openai');
        cy.get('#model_name').type('gpt-4');
        cy.get('#sidePanel form').find('button[type="submit"]').click();

        cy.get('#model-builder-modal').should('be.visible');
        cy.get('#model-builder-modal').contains('but is asked');
    });
});
