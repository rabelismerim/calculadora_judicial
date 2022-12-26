import Vue from 'vue'
import App from './App.vue'
import router from './router'
import 'vuetify/dist/vuetify.min.css'
import * as VueGoogleMaps from 'vue2-google-maps'
import axios from './plugins/axios'
import axios_ext from 'axios'
import Utils from './plugins/utils'
import store from './store'
import vuetify from './plugins/vuetify'
import serviceContainer from './service-container';




Vue.config.productionTip = false
Vue.prototype.$http = axios;
Vue.prototype.$http_ext = axios_ext;
Vue.prototype.$fadlUtils = Utils


Vue.use(VueGoogleMaps, {
  load: {
    key: 'AIzaSyDwvny7Wj1cTgM_GgoaYGTtz94VQWPxvRw',
    libraries: 'places,geocoder',
  },
  installComponents: true
});

new Vue({
  store,
  router,
  vuetify,
  provide: serviceContainer,
  render: h => h(App)
}).$mount('#app')

