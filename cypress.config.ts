import { defineConfig } from 'cypress';

export default defineConfig({
    watchForFileChanges: false,
    viewportWidth: 1920,
    viewportHeight: 1080,
    e2e: {
        baseUrl: 'http://localhost:8000/',
        specPattern: 'cypress/e2e/**/*.spec.ts',
    },
});
