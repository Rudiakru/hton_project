module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        risk: {
          winning: '#10B981',    // Green
          competitive: '#F59E0B', // Yellow
          vulnerable: '#F97316',  // Orange
          critical: '#EF4444',    // Red
        },
        brand: {
          primary: '#3b82f6',
          dark: '#111827',
          light: '#f3f4f6',
        }
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
