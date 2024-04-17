/// <reference types="cypress" />

describe('Quiz tests', () => {
    beforeEach(() => cy.visit('/'));
    it('Should navigate through quiz', () => {
        cy.title().should('eq', 'e-footprint');
        cy.get('#quiz-link').click();
        cy.get('#main-content-block h1').should('have.text', 'Start mapping your service');
        cy.get('#go-to-user-journeys-button').click();
        cy.url().should('eq', `${Cypress.config('baseUrl')}quiz/user-journeys`);
        cy.get('#validate-user-journeys-form-button').click();
        cy.url().should('eq', `${Cypress.config('baseUrl')}quiz/services`);
        cy.get('#validate-services-form-button').click();
        cy.url().should('eq', `${Cypress.config('baseUrl')}quiz/usage-patterns`);
        cy.get('#validate-usage-patterns-form-button').click();

        //cy.url().should('eq', `${Cypress.config('baseUrl')}analyze/`);
    });
});
