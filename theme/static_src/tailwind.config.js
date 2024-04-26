/**
 * This is a minimal config.
 *
 * If you need the full config, get it from here:
 * https://unpkg.com/browse/tailwindcss@latest/stubs/defaultConfig.stub.js
 */

module.exports = {
  content: [
    /**
     * HTML. Paths to Django template files that will contain Tailwind CSS classes.
     */

    /*  Templates within theme app (<tailwind_app_name>/templates), e.g. base.html. */
    "../templates/**/*.html",

    /*
     * Main templates directory of the project (BASE_DIR/templates).
     * Adjust the following line to match your project structure.
     */
    "../../templates/**/*.html",

    /*
     * Templates in other django apps (BASE_DIR/<any_app_name>/templates).
     * Adjust the following line to match your project structure.
     */
    "../../**/templates/**/*.html",

    /**
     * JS: If you use Tailwind CSS in JavaScript, uncomment the following lines and make sure
     * patterns match your project structure.
     */
    /* JS 1: Ignore any JavaScript in node_modules folder. */
    // '!../../**/node_modules',
    /* JS 2: Process all JavaScript files in the project. */
    // '../../**/*.js',

    /**
     * Python: If you use Tailwind CSS classes in Python, uncomment the following line
     * and make sure the pattern below matches your project structure.
     */
    // '../../**/*.py'
  ],
  theme: {
    colors: {
      "grey-1": "#ffffff",
      "grey-2": "#686868",
      "grey-3": "#494646",
      "grey-4": "#bdbdbd",
      "grey-5": "#424242",
      "grey-6": "#2c2c2c",
      "grey-7": "#7f7c7c",
      "grey-8": "#b1b1b1",
      "grey-9": "#49464680",
      "grey-10": "#696666",
      "grey-11": "#2e2e2e",
      "grey-12": "#404040",
      "grey-13": "#e7e7e7",
      "grey-14": "#4f4d4d",
      "grey-15": "#f1f1f180",
      "grey-16": "#f4f4f4",
      "white-1": "#f8f8f8",
      "black-1": "#181818",
      white: "#fff",
      black: "#000000",
      primary: "#5E2FFB",
      "primary-light": "#9E82FD",
      "primary-lighter": "#DFD5FE",
      "primary-dark": "#35179C",
      "primary-darker": "#261365",
      secondary: "#F7AB27",
      "secondary-light": "#FFCD6C",
      "background-1": "#1F1A32",
      "background-2": "#322D46",
       "background-3": "#433E58",
       "background-4": "#F9F7FF",
       "menubar": "#0A051B",
       "pink-light": "#CFC1FE",
       "red-1": "#F00"
    },
  },
  plugins: [
    /**
     * '@tailwindcss/forms' is the forms plugin that provides a minimal styling
     * for forms. If you don't like it or have own styling for forms,
     * comment the line below to disable '@tailwindcss/forms'.
     */
    require("@tailwindcss/forms"),
    require("@tailwindcss/typography"),
    require("@tailwindcss/aspect-ratio"),
  ],
};
