// ***********************************************
// This example commands.js shows you how to
// create various custom commands and overwrite
// existing commands.
//
// For more comprehensive examples of custom
// commands please read more here:
// https://on.cypress.io/custom-commands
// ***********************************************
//
//
// -- This is a parent command --
// Cypress.Commands.add('login', (email, password) => { ... })
//
//
// -- This is a child command --
// Cypress.Commands.add('drag', { prevSubject: 'element'}, (subject, options) => { ... })
//
//
// -- This is a dual command --
// Cypress.Commands.add('dismiss', { prevSubject: 'optional'}, (subject, options) => { ... })
//
//
// -- This will overwrite an existing command --
// Cypress.Commands.overwrite('visit', (originalFn, url, options) => { ... })

import addContext = require('mochawesome/addContext');

// Import commands.ts using ES2015 syntax:
import './commands';

import { Suite, Test } from 'mocha';

// Alternatively you can use CommonJS syntax:
// require('./commands')

// https://medium.com/egnyte-engineering/3-steps-to-awesome-test-reports-with-cypress-f4fe915bc246
Cypress.on('test:after:run', (test, runnable) => {
  if (test.state === 'failed') {
    let item: Test | Suite = runnable;
    const nameParts = [runnable.title];

    // Iterate through all parents and grab the titles
    while (item.parent) {
      nameParts.unshift(item.parent.title);
      item = item.parent;
    }

    const fullTestName = nameParts.filter(Boolean).join(' -- '); // this is how cypress joins the test title fragments
    const imageUrl = `screenshots/${Cypress.spec.relative.replace(
      'cypress/e2e/',
      ''
    )}/${fullTestName} (failed).png`;

    addContext({ test }, imageUrl);
  }
});
