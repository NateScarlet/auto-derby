module.exports = {
  important: '#h',
  content: ['./src/**/*.{vue,ts}'],
  theme: {
    extend: {
      colors: {
        theme: {
          text: '#794016',
          green: '#99da08',
        },
      },
    },
  },
  plugins: [require('@tailwindcss/forms')],
};
