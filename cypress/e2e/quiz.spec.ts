/// <reference types="cypress" />

describe('Quiz tests', () => {
    beforeEach(() => cy.visit('/'));
    it('Should navigate through quiz', () => {
        cy.title().should('eq', 'e-footprint');
        cy.get('#quiz-link').click();
        cy.get('#main-content-block h1').should('have.text', 'Start mapping your service');
        cy.get('#go-to-user-journeys-button').click();
        cy.url().should('eq', `${Cypress.config('baseUrl')}quiz/user-journeys`);


        cy.get("input[type=text]").eq(0).type("Do a search");
        cy.get("input[type=number]").eq(0).type(1);
        cy.get("input[type=text]").eq(1).type("Watch a video");
        cy.get("input[type=number]").eq(1).type(10);
        cy.get("input[type=text]").eq(2).type("Write a comment");
        cy.get("input[type=number]").eq(2).type(2);
        cy.get('#validate-user-journeys-form-button').click();
        cy.url().should('eq', `${Cypress.config('baseUrl')}quiz/services`);

        cy.get("select").eq(0).select("Web Application");
        cy.get("select").eq(1).select("Streaming");
        cy.get("select").eq(2).select("Gen AI");

        cy.get('#validate-services-form-button').click();
        cy.url().should('eq', `${Cypress.config('baseUrl')}quiz/usage-patterns`);

        cy.get("input").type("100");
        cy.get("select[name='device']").select("Laptop")
        cy.get("select[name='country']").select("France")
        cy.get('#validate-usage-patterns-form-button').click();
        cy.url().should('eq', `${Cypress.config('baseUrl')}model_builder/`);
    });
});
