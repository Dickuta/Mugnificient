const { configure } = require('quasar/wrappers');

module.exports = configure(function (ctx) {
  return {
    boot: ['api'],
    
    css: ['app.css'],
    
    extras: [
      'roboto-font',
      'material-icons',
    ],

    build: {
      target: {
        browser: [ 'es2019', 'edge88', 'firefox78', 'chrome87', 'safari13.1' ]
      },
      
      vueRouterMode: 'history',
    },

    devServer: {
      open: false,
      port: 9000,
    },

    framework: {
      config: {
        brand: {
          primary: process.env.VITE_APP_PRIMARY_COLOR || '#003366',
          secondary: process.env.VITE_APP_SECONDARY_COLOR || '#D4AF37',
          accent: process.env.VITE_APP_ACCENT_COLOR || '#003366',
          dark: '#1d1d1d',
          positive: '#21BA45',
          negative: '#C10015',
          info: '#31CCEC',
          warning: '#F2C037'
        }
      },
      plugins: [
        'Notify'
      ]
    },

    animations: [],

    ssr: {
      pwa: false,
      prodPort: 3000,
    },
    
    pwa: {
      workboxMode: 'GenerateSW',
    },
    
    capacitor: {
      hideSplashscreen: true,
    },
    
    electron: {
      inspectPort: 5858,
      bundler: 'packager',
    },
    
    bex: {
      contentScripts: [
        'my-content-script'
      ]
    }
  };
});
