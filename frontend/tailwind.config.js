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
          950: '#f8fafc',
          900: '#ffffff',
          850: '#f1f5f9',
          800: '#e2e8f0',
          700: '#cbd5e1',
          600: '#94a3b8',
          500: '#64748b',
          400: '#475569',
          300: '#334155',
          200: '#1e293b',
          100: '#0f172a',
          50: '#020617',
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
