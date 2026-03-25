import { configure } from 'quasar/wrappers';

export default configure(function () {
  return {
    boot: ['api'],
    css: ['app.css'],
    extras: ['roboto-font', 'material-icons'],
    build: {
      target: { browser: ['es2019', 'edge88', 'firefox78', 'chrome87', 'safari13.1'] },
      vueRouterMode: 'history',
    },
    devServer: { open: false, port: 9000 },
    framework: { config: {}, plugins: ['Notify'] },
    animations: [],
    ssr: { pwa: false, prodPort: 3000 },
    pwa: { workboxMode: 'GenerateSW' },
    capacitor: { hideSplashscreen: true },
    electron: { inspectPort: 5858, bundler: 'packager' },
    bex: { contentScripts: ['my-content-script'] },
  };
});
