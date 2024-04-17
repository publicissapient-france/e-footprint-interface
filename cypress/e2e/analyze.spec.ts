/// <reference types="cypress" />

import { Interception } from 'cypress/types/net-stubbing';

describe('Analyze tests', () => {
    beforeEach(() => cy.visit('/model_builder'));

    it('Should create new usage pattern', () => {
        const objectType = 'UserJourney';
        cy.get('#object-creation-form').should('not.be.visible');
        cy.get(`.UserJourney`).should('have.length', 1);
        cy.get(`#add-new-UserJourney-button`).click();
        cy.get('#object-creation-form').should('be.visible');
        cy.get('#object-creation-form h3').should('have.text', `New UserJourney`);
        cy.get('#new-object-name').clear().type(`New UserJourney`);
        cy.get('#uj_steps input').eq(0).click();
        cy.intercept('*/add-new-object').as('addNewObject');
        cy.get('#create-new-object-button').scrollIntoView().click();
        cy.wait('@addNewObject').then((response: Interception) => {
            cy.get(`.UserJourney`).should('have.length', 2);
        });
    });
    it('Should create new user journey', () => {
        cy.get('#object-creation-form').should('not.be.visible');
        cy.get(`.UserJourney`).should('have.length', 1);
        cy.get(`#add-new-UserJourney-button`).click();
        cy.get('#object-creation-form').should('be.visible');
        cy.get('#object-creation-form h3').should('have.text', `New UserJourney`);
        cy.get('#new-object-name').clear().type(`New UserJourney`);
        cy.get('#uj_steps input').eq(0).click();
        cy.intercept('*/add-new-object').as('addNewObject');
        cy.get('#create-new-object-button').scrollIntoView().click();
        cy.wait('@addNewObject').then((response: Interception) => {
            cy.get(`.UserJourney`).should('have.length', 2);
        });
    });
    it('Should create new service', () => {
        cy.get('#object-creation-form').should('not.be.visible');
        cy.get(`.Service`).should('have.length', 1);
        cy.get(`#add-new-Service-button`).click();
        cy.get('#object-creation-form').should('be.visible');
        cy.get('#object-creation-form h3').should('have.text', `New Service`);
        cy.get('#new-object-name').clear().type(`New Service`);
        cy.intercept('*/add-new-object').as('addNewObject');
        cy.get('#create-new-object-button').scrollIntoView().click();
        cy.wait('@addNewObject').then((response: Interception) => {
            cy.get(`.Service`).should('have.length', 2);
        });
    });
    it('Should create new autoscaling', () => {
        cy.get('#object-creation-form').should('not.be.visible');
        cy.get(`.Autoscaling`).should('have.length', 1);
        cy.get(`#add-new-Autoscaling-button`).click();
        cy.get('#object-creation-form').should('be.visible');
        cy.get('#object-creation-form h3').should('have.text', `New Autoscaling`);
        cy.get('#new-object-name').clear().type(`New Autoscaling`);
        cy.intercept('*/add-new-object').as('addNewObject');
        cy.get('#create-new-object-button').scrollIntoView().click();
        cy.wait('@addNewObject').then((response: Interception) => {
            cy.get(`.Autoscaling`).should('have.length', 2);
        });
    });
    it('Should create new storage', () => {
        cy.get('#object-creation-form').should('not.be.visible');
        cy.get(`.Storage`).should('have.length', 1);
        cy.get(`#add-new-Storage-button`).click();
        cy.get('#object-creation-form').should('be.visible');
        cy.get('#object-creation-form h3').should('have.text', `New Storage`);
        cy.get('#new-object-name').clear().type(`New Storage`);
        cy.intercept('*/add-new-object').as('addNewObject');
        cy.get('#create-new-object-button').scrollIntoView().click();
        cy.wait('@addNewObject').then((response: Interception) => {
            cy.get(`.Storage`).should('have.length', 2);
        });
    });
    it('Should create new hardware', () => {
        cy.get('#object-creation-form').should('not.be.visible');
        cy.get(`.Hardware`).should('have.length', 1);
        cy.get(`#add-new-Hardware-button`).click();
        cy.get('#object-creation-form').should('be.visible');
        cy.get('#object-creation-form h3').should('have.text', `New Hardware`);
        cy.get('#new-object-name').clear().type(`New Hardware`);
        cy.intercept('*/add-new-object').as('addNewObject');
        cy.get('#create-new-object-button').scrollIntoView().click();
        cy.wait('@addNewObject').then((response: Interception) => {
            cy.get(`.Hardware`).should('have.length', 2);
        });
    });
    it('Should create new network', () => {
        cy.get('#object-creation-form').should('not.be.visible');
        cy.get(`.Network`).should('have.length', 1);
        cy.get(`#add-new-Network-button`).click();
        cy.get('#object-creation-form').should('be.visible');
        cy.get('#object-creation-form h3').should('have.text', `New Network`);
        cy.get('#new-object-name').clear().type(`New Network`);
        cy.intercept('*/add-new-object').as('addNewObject');
        cy.get('#create-new-object-button').scrollIntoView().click();
        cy.wait('@addNewObject').then((response: Interception) => {
            cy.get(`.Network`).should('have.length', 2);
        });
    });

    it('Should edit an object', () => {
        cy.get('#UsagePattern-section .edit-object-button').eq(0).click();
    });
});
