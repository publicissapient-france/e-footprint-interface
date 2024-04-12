/// <reference types="cypress" />

import { Interception } from 'cypress/types/net-stubbing';

describe('Analyze tests', () => {
    beforeEach(() => cy.visit('/model_builder'));

    xit('Should create new system', () => createNewObject('System'));
    it('Should create new usage pattern', () => createNewObject('UsagePattern'));
    it('Should create new service', () => createNewObject('Service'));
    xit('Should create new autoscaling', () => createNewObject('Autoscaling'));
    xit('Should create new storage', () => createNewObject('Storage'));
    it('Should create new hardware', () => createNewObject('Hardware'));
    it('Should create new network', () => createNewObject('Network'));

    function createNewObject(objectType: string) {
        cy.get('#object-creation-form').should('not.be.visible');
        cy.get(`.${objectType}`).should('have.length', 1);
        cy.get(`#add-new-${objectType}-button`).click();
        cy.get('#object-creation-form').should('be.visible');
        cy.get('#object-creation-form > h3').should('have.text', `New ${objectType}`);
        cy.get('#new-object-name').clear().type(`New ${objectType}`);
        cy.intercept('*/add-new-object').as('addNewObject');
        cy.get('#create-new-object-button').scrollIntoView().click();
        cy.wait('@addNewObject').then((response: Interception) => {
            cy.get(`.${objectType}`).should('have.length', 2);
        });
    }
});
