/// <reference types="cypress" />

describe('Analyze tests', () => {
    beforeEach(() => cy.visit('/model_builder'));

    it('Should create new system', () => {
        cy.title().should('eq', 'e-footprint');
        cy.get('#object-creation-form').should('not.be.visible');
        cy.get('#add-new-System-button').click();
        cy.get('#object-creation-form').should('be.visible');
        cy.get('#object-creation-form > h3').should('have.text', 'New System');
        cy.get('#new-object-name').clear().type('New System');
        cy.get('#create-new-object-button').click();
    });

    xit('Should create new usage pattern', () => {
        cy.title().should('eq', 'e-footprint');
        cy.get('#object-creation-form').should('not.be.visible');
        cy.get('#add-new-UsagePattern-button').click();
        cy.get('#object-creation-form').should('be.visible');
        cy.get('#object-creation-form > h3').should('have.text', 'New UsagePattern');
        cy.get('#new-object-name').clear().type('New Usage Pattern');
        cy.get('#create-new-object-button').click();
    });
});
