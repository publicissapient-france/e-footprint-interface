/// <reference types="cypress" />

describe('Quiz tests', () => {
  beforeEach(() => cy.visit('/'));
  it('Test home', () => {
    cy.title().should('eq', 'e-footprint');
  });
});
