const { defineConfig } = require("cypress");


module.exports = defineConfig({
  e2e: {
    baseUrl: "http://localhost:8000/",
    viewportWidth: 1920,   // Largeur en pixels
    viewportHeight: 1080,
    setupNodeEvents(on, config) {
    },
  }
});
