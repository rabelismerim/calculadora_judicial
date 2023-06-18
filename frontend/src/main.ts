import { createApp } from 'vue'
import { autoAnimatePlugin } from '@formkit/auto-animate/vue'
import { Dialog, Quasar, Ripple } from 'quasar'
import quasarLang from 'quasar/lang/pt-BR'
import quasarIconSet from 'quasar/icon-set/material-icons-outlined'
import router from './router'
import App from './App.vue'

import '@quasar/extras/material-icons-outlined/material-icons-outlined.css'
import 'quasar/src/css/index.sass'
import '@/assets/style.css'
import '@unocss/reset/tailwind.css'
import 'uno.css'

const app = createApp(App)

app.use(Quasar, {
  plugins: {
    Dialog,
  }, // import Quasar plugins and add here
  lang: quasarLang,
  iconSet: quasarIconSet,
})
app.directive('ripple', Ripple)
app.directive('resize', vResize)
app.use(router)
app.use(autoAnimatePlugin)

app.mount('#app')
