/** @type {import('tailwindcss').Config} */
export default {
  darkMode: 'class',
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        // Neutral surfaces tuned for dark UI layering
        surface: {
          0: '#0d0f15',
          50: '#11141b',
          100: '#161b23',
          200: '#1e252f',
          300: '#28313d',
          400: '#34404f'
        },
        accent: {
          blue: '#3b82f6',
          purple: '#7c3aed',
          cyan: '#06b6d4'
        },
        glass: 'rgba(255,255,255,0.04)'
      },
      boxShadow: {
        'elevated-sm': '0 1px 2px 0 rgba(0,0,0,0.4), 0 0 0 1px rgba(255,255,255,0.03)',
        'elevated': '0 4px 16px -2px rgba(0,0,0,0.55), 0 0 0 1px rgba(255,255,255,0.04)',
        'elevated-lg': '0 8px 32px -4px rgba(0,0,0,0.6), 0 0 0 1px rgba(255,255,255,0.05)',
        'glow-blue': '0 0 0 1px rgba(56,189,248,0.25), 0 4px 16px -2px rgba(56,189,248,0.4)',
        'inner-glow': 'inset 0 0 0 1px rgba(255,255,255,0.05), inset 0 1px 4px 0 rgba(255,255,255,0.06)'
      },
      backdropBlur: {
        xs: '2px'
      },
      animation: {
        'fade-in': 'fade-in .25s ease-out',
        'scale-in': 'scale-in .25s cubic-bezier(.4,0,.2,1)'
      },
      keyframes: {
        'fade-in': { '0%': { opacity: 0 }, '100%': { opacity: 1 } },
        'scale-in': { '0%': { opacity: 0, transform: 'scale(.96)' }, '100%': { opacity: 1, transform: 'scale(1)' } }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif']
      },
      borderRadius: {
        xl: '1rem'
      }
    },
  },
  plugins: [],
};
