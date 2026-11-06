/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        paypal: {
          navy: '#003087',
          navyDark: '#001C64',
          blue: '#0070BA',
          sky: '#E8F3FF',
          canvas: '#F5F7FA',
          ink: '#0C121D',
          slate: '#4A5568',
          muted: '#718096',
          border: '#E2E8F0',
        },
      },
    },
  },
  plugins: [],
};
