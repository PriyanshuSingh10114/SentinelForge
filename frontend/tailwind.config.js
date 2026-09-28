/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        sentinel: {
          950: '#070a0f',
          900: '#0c1017',
          850: '#111722',
          800: '#161e2c',
          700: '#222f44',
          600: '#334460',
          500: '#485e84',
          400: '#647ea9',
          300: '#8ba2ce',
          200: '#b8c9e8',
          100: '#dce5f5',
          50: '#f0f4fa',
        },
        cyber: {
          critical: '#ef4444',
          high: '#f97316',
          medium: '#eab308',
          low: '#3b82f6',
          info: '#64748b',
          success: '#10b981',
          cyan: '#06b6d4',
          violet: '#8b5cf6',
        }
      },
      fontFamily: {
        mono: ['JetBrains Mono', 'Fira Code', 'monospace'],
        sans: ['Inter', 'system-ui', 'sans-serif'],
      }
    },
  },
  plugins: [],
}
