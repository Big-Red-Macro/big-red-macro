/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
      },
      colors: {
        'cornell-red': '#B31B1B',
        'cornell': {
          50:  '#fef2f2',
          100: '#fde3e3',
          200: '#fccbcb',
          300: '#f9a8a8',
          400: '#f37575',
          500: '#e84848',
          600: '#d52b2b',
          700: '#B31B1B',  // official Cornell Red
          800: '#941a1a',
          900: '#7b1c1c',
          950: '#430a0a',
        },
        slate: {
          850: '#151e2e',
          900: '#0f172a',
        }
      },
      animation: {
        'fade-in': 'fadeIn 0.5s ease-out',
        'slide-up': 'slideUp 0.5s ease-out',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { opacity: '0', transform: 'translateY(20px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
      },
    },
  },
  plugins: [],
}
