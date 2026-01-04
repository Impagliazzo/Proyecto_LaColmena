/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './templates/**/*.html',
    './usuarios/templates/**/*.html',
    './propiedades/templates/**/*.html',
    './contactos/templates/**/*.html',
    './suscripciones/templates/**/*.html',
    './notificaciones/templates/**/*.html',
  ],
  theme: {
    extend: {
      colors: {
        'primary': '#FBBF24', // Yellow-400
        'primary-dark': '#F59E0B', // Yellow-500
        'secondary': '#3B82F6', // Blue-500
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
