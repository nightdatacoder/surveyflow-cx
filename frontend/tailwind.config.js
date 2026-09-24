/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ['./index.html', './src/**/*.{vue,js,ts}'],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Montserrat', 'sans-serif'],
      },
      colors: {
        mtn: {
          yellow: '#FFCC00',
          'yellow-hover': '#F0BE00',
          blue: '#003399',
          'blue-light': '#0044CC',
        },
        surface: '#FFFFFF',
        canvas: '#F4F5F7',
        border: '#E8E9EC',
      },
      borderRadius: {
        xl: '12px',
        '2xl': '16px',
        '3xl': '20px',
      },
      boxShadow: {
        card: '0 1px 3px rgba(0,0,0,.04), 0 1px 2px rgba(0,0,0,.03)',
        'card-hover': '0 4px 12px rgba(0,0,0,.08)',
        yellow: '0 4px 12px rgba(255,204,0,.3)',
      }
    }
  },
  plugins: []
}
