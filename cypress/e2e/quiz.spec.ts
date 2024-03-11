/// <reference types="cypress" />

describe('Quiz tests', () => {
  beforeEach(() => cy.visit('/quiz'));
  it('Test quiz', () => {
    cy.title().should('eq', 'e-footprint');
  });
});
