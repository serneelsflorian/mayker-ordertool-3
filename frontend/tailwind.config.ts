import type { Config } from 'tailwindcss';

const config: Config = {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        brand: {
          teal: '#269A91',
          'teal-hover': '#1f857d',
          coral: '#D44858',
          'coral-hover': '#b93b48',
          bluegrey: '#9ABFCB',
          taupe: '#A39286',
          'bg-soft': '#F6F4F1',
        },
      },
    },
  },
  plugins: [],
};

export default config;
