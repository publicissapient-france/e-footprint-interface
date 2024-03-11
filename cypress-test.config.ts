import { defineConfig } from 'cypress';

export default defineConfig({
  watchForFileChanges: false,
  defaultCommandTimeout: 6000,
  viewportWidth: 1920,
  viewportHeight: 1080,
  screenshotOnRunFailure: true,
  video: false,
  videoCompression: false,
  reporter: 'cypress-multi-reporters',
  reporterOptions: {
    configFile: 'reporter-e2e-config.json',
  },
  e2e: {
    setupNodeEvents(on, config) {
      return require('./cypress/plugins/index.ts')(on, config);
    },
    baseUrl: 'http://localhost:8000/',
    specPattern: 'cypress/e2e/**/*.spec.ts',
  },
});
