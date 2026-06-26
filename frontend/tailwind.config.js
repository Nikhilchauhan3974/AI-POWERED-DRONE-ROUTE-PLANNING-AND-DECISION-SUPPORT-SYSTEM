/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        cyber: {
          bg: '#020617',     // slate-950
          dark: '#0b1329',   // deep command space
          panel: 'rgba(15, 23, 42, 0.75)', // glass backdrop
          border: '#1e293b',  // slate-800
          cyan: '#06b6d4',   // neon cyan
          amber: '#f59e0b',  // warning amber
          red: '#ef4444',    // alarm red
          green: '#10b981',  // safe green
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['Consolas', 'Fira Code', 'monospace'],
      },
      boxShadow: {
        'neon-cyan': '0 0 15px rgba(6, 182, 212, 0.5)',
        'neon-amber': '0 0 15px rgba(245, 158, 11, 0.5)',
        'neon-red': '0 0 15px rgba(239, 68, 68, 0.5)',
        'neon-green': '0 0 15px rgba(16, 185, 129, 0.5)',
        'glass': '0 8px 32px 0 rgba(0, 0, 0, 0.37)',
      }
    },
  },
  plugins: [],
}
