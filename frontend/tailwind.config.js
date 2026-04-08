/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        smvec: {
          blue: '#003087',
          gold: '#FFD700',
          lightblue: '#0066CC',
          darkblue: '#001a4d',
        }
      }
    }
  },
  plugins: [],
}
