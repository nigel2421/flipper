/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./publications/templates/**/*.html",
    "./templates/**/*.html",
    "./static/**/*.js",
  ],
  theme: {
    extend: {
      colors: {
        'primary-blue': '#0D6EFD', // Business Blue
        'accent-yellow': '#FFC107', // Gold highlight
        'dark-bg': '#0a192f',
      },
      fontFamily: {
        // "Leaders of the field" - newspaper standard
        'serif': ['Merriweather', 'Georgia', 'serif'],
        'sans': ['Inter', 'system-ui', 'sans-serif'],
      },
      lineClamp: {
        2: '2',
        3: '3',
      },
    },
  },
  plugins: [],
}
