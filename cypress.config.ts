import { defineConfig } from 'cypress';

export default defineConfig({
  watchForFileChanges: false,
  e2e: {
    baseUrl: 'http://localhost:8000/',
    specPattern: 'cypress/e2e/**/*.spec.ts',
  },
});
