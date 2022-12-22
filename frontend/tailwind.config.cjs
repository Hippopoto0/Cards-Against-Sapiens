/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      backgroundColor: {
        "primary": "#ffffff",
        "secondary": "#dee2e6",
      },
      textColor: {
        "primary": "#dee2e6",
      },
    },
    screens: {
      'xs': '500px',
      'sm': '700px',
      // => @media (min-width: 640px) { ... }

      'md': '912px',
      // => @media (min-width: 768px) { ... }

      'lg': '1024px',
      // => @media (min-width: 1024px) { ... }

      'xl': '1280px',
      // => @media (min-width: 1280px) { ... }

      '2xl': '1536px',
      // => @media (min-width: 1536px) { ... }
    }
  },
  plugins: [],
}
