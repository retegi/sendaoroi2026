/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./templates/**/*.html",
    "./pages/templates/**/*.html",
    "./**/templates/**/*.html",
    "./pages/**/*.py",
    "./config/**/*.py",
  ],
  theme: {
    extend: {
      colors: {
        "sendaoroi-blue": "#1A4C5D",
        "sendaoroi-green": "#8B9D8C",
        "sendaoroi-gray": "#8E8880",
        "sendaoroi-sand": "#D8CAB3",
        brand: {
          teal: "#1A4C5D",
          moss: "#8B9D8C",
          stone: "#8E8880",
          sand: "#D8CAB3",
          gray: "#8E8880",
        },
      },
    },
  },
  plugins: [],
};
