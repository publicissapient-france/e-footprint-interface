/// <reference types="cypress" />

import { Interception } from 'cypress/types/net-stubbing';

describe('Analyze tests', () => {
    beforeEach(() => cy.visit('/model_builder'));

    it('Should create new usage pattern', () => {
        cy.get('#object-creation-or-edition-form').should('not.exist');
        cy.get(`.drawflow-node.UsagePattern`).should('have.length', 1);
        cy.get(`#add-new-UsagePattern-button`).click();
        cy.get('#object-creation-or-edition-form').should('be.visible');
        cy.get('#object-creation-or-edition-form h3').should('have.text', `New UsagePattern`);
        cy.get('#new-object-name').clear().type(`New UsagePattern`);
        cy.intercept('*/add-new-object').as('addNewObject');
        cy.get('#create-new-object-button').click();
        cy.wait('@addNewObject').then((response: Interception) => {
            expect(response.response.statusCode).to.eq(200)
            cy.get(`.drawflow-node.UsagePattern`).should('have.length', 2);
        });
    });
    it('Should create new user journey', () => {
        cy.get('#object-creation-or-edition-form').should('not.exist');
        cy.get(`.drawflow-node.UserJourney`).should('have.length', 1);
        cy.get(`#add-new-UserJourney-button`).click();
        cy.get('#object-creation-or-edition-form').should('be.visible');
        cy.get('#object-creation-or-edition-form h3').should('have.text', `New UserJourney`);
        cy.get('#new-object-name').clear().type(`New UserJourney`);
        cy.get('#uj_steps input').eq(0).click();
        cy.intercept('*/add-new-object').as('addNewObject');
        cy.get('#create-new-object-button').click();
        cy.wait('@addNewObject').then((response: Interception) => {
            expect(response.response.statusCode).to.eq(200)
            cy.get(`.drawflow-node.UserJourney`).should('have.length', 2);
        });
    });
    it('Should create new service', () => {
        cy.get('#object-creation-or-edition-form').should('not.exist');
        cy.get(`.drawflow-node.Service`).should('have.length', 1);
        cy.get(`#add-new-Service-button`).click();
        cy.get('#object-creation-or-edition-form').should('be.visible');
        cy.get('#object-creation-or-edition-form h3').should('have.text', `New Service`);
        cy.get('#new-object-name').clear().type(`New Service`);
        cy.intercept('*/add-new-object').as('addNewObject');
        cy.get('#create-new-object-button').click();
        cy.wait('@addNewObject').then((response: Interception) => {
            expect(response.response.statusCode).to.eq(200)
            cy.get(`.drawflow-node.Service`).should('have.length', 2);
        });
    });
    it('Should create new autoscaling', () => {
        cy.get('#object-creation-or-edition-form').should('not.exist');
        cy.get(`.drawflow-node.Autoscaling`).should('have.length', 1);
        cy.get(`#add-new-Autoscaling-button`).click();
        cy.get('#object-creation-or-edition-form').should('be.visible');
        cy.get('#object-creation-or-edition-form h3').should('have.text', `New Autoscaling`);
        cy.get('#new-object-name').clear().type(`New Autoscaling`);
        cy.intercept('*/add-new-object').as('addNewObject');
        cy.get('#create-new-object-button').click();
        cy.wait('@addNewObject').then((response: Interception) => {
            expect(response.response.statusCode).to.eq(200)
            cy.get(`.drawflow-node.Autoscaling`).should('have.length', 2);
        });
    });
    it('Should create new storage', () => {
        cy.get('#object-creation-or-edition-form').should('not.exist');
        cy.get(`.drawflow-node.Storage`).should('have.length', 1);
        cy.get(`#add-new-Storage-button`).click();
        cy.get('#object-creation-or-edition-form').should('be.visible');
        cy.get('#object-creation-or-edition-form h3').should('have.text', `New Storage`);
        cy.get('#new-object-name').clear().type(`New Storage`);
        cy.intercept('*/add-new-object').as('addNewObject');
        cy.get('#create-new-object-button').click();
        cy.wait('@addNewObject').then((response: Interception) => {
            expect(response.response.statusCode).to.eq(200)
            cy.get(`.drawflow-node.Storage`).should('have.length', 2);
        });
    });
    it('Should create new hardware', () => {
        cy.get('#object-creation-or-edition-form').should('not.exist');
        cy.get(`.drawflow-node.Hardware`).should('have.length', 1);
        cy.get(`#add-new-Hardware-button`).click();
        cy.get('#object-creation-or-edition-form').should('be.visible');
        cy.get('#object-creation-or-edition-form h3').should('have.text', `New Hardware`);
        cy.get('#new-object-name').clear().type(`New Hardware`);
        cy.intercept('*/add-new-object').as('addNewObject');
        cy.get('#create-new-object-button').click();
        cy.wait('@addNewObject').then((response: Interception) => {
            expect(response.response.statusCode).to.eq(200)
            cy.get(`.drawflow-node.Hardware`).should('have.length', 2);
        });
    });
    it('Should create new network', () => {
        cy.get('#object-creation-or-edition-form').should('not.exist');
        cy.get(`.drawflow-node.Network`).should('have.length', 1);
        cy.get(`#add-new-Network-button`).click();
        cy.get('#object-creation-or-edition-form').should('be.visible');
        cy.get('#object-creation-or-edition-form h3').should('have.text', `New Network`);
        cy.get('#new-object-name').clear().type(`New Network`);
        cy.intercept('*/add-new-object').as('addNewObject');
        cy.get('#create-new-object-button').click();
        cy.wait('@addNewObject').then((response: Interception) => {
            expect(response.response.statusCode).to.eq(200)
            cy.get(`.drawflow-node.Network`).should('have.length', 2);
        });
    });

    it('Should edit an Usage pattern', () => {
        cy.get(`.drawflow-node.UserJourney`).should('have.length', 1);
        cy.get(`#add-new-UserJourney-button`).click();
        cy.get('#new-object-name').clear().type(`New UserJourney`);
        cy.get('#uj_steps input').eq(0).click();
        cy.intercept('*/add-new-object').as('addNewObject');
        cy.get('#create-new-object-button').click();
        cy.wait('@addNewObject').then((response: Interception) => {
            expect(response.response.statusCode).to.eq(200)
            cy.get(`.drawflow-node.UserJourney`).should('have.length', 2);
            cy.get(`.drawflow-node.UserJourney`).eq(1).find('.object-name').should('have.text', 'New UserJourney');
        });
        cy.get('.drawflow-node.UsagePattern').eq(0).find(".edit-object-button").click();
        cy.get('#object-creation-or-edition-form #user_journey').select('New UserJourney');
        cy.intercept('*/edit-object').as('editObject');
        cy.get('#create-new-object-button').click();
    });

    it('Should add an object then delete it', () => {
        cy.get(`.drawflow-node.UsagePattern`).should('have.length', 1);
        cy.get(`#add-new-UsagePattern-button`).click();
        cy.get('#new-object-name').clear().type(`New UsagePattern`);
        cy.intercept('*/add-new-object').as('addNewObject');
        cy.get('#create-new-object-button').click();
        cy.wait('@addNewObject').then((response: Interception) => {
            expect(response.response.statusCode).to.eq(200)
            cy.intercept('*/delete-object').as('deleteObject');
            cy.get(`.drawflow-node.UsagePattern`).eq(1).get('.delete-object-button').eq(0).click();
            cy.wait('@deleteObject').then((deleteObjectResponse: Interception) => {
                cy.get(`.drawflow-node.UsagePattern`).should('have.length', 1);
            });
        });
    });
});
