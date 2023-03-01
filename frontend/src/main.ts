import { createApp } from 'vue'
import { autoAnimatePlugin } from '@formkit/auto-animate/vue'
import { createRouter, createWebHistory } from 'vue-router'
import { setupLayouts } from 'virtual:generated-layouts'
import { Quasar, Ripple } from 'quasar'
import quasarLang from 'quasar/lang/pt-BR'
import quasarIconSet from 'quasar/icon-set/material-icons-outlined'
import App from './App.vue'

import generatedRoutes from '~pages'

import '@quasar/extras/material-icons-outlined/material-icons-outlined.css'
import 'quasar/src/css/index.sass'
import '@/assets/style.css'
import '@unocss/reset/tailwind.css'
import 'uno.css'

const app = createApp(App)

const routes = setupLayouts(generatedRoutes)
  .map((route: any, index: number) => {
    route.meta = generatedRoutes[index].meta || {}
    return route
  })

const router = createRouter({
  history: createWebHistory(import.meta.env.VITE_ROUTER_BASE_URL),
  routes,
})

router.beforeEach(async (to, from, next) => {
  if (!to.meta?.authentication) {
    next()
    return
  }
  const { authorized } = await usersService.getMyProfile()
  if (authorized)
    next()
  else
    next('/')
})

app.use(Quasar, {
  plugins: {}, // import Quasar plugins and add here
  lang: quasarLang,
  iconSet: quasarIconSet,
})
app.directive('ripple', Ripple)
app.use(router)
app.use(autoAnimatePlugin)

app.mount('#app')
