import Vue from 'vue'
import VueRouter from 'vue-router'

import routes from './routes'

import store from '../store'

Vue.use(VueRouter)

const DEFAULT_TITLE = 'aplication'


const router = new VueRouter({
  mode: 'history',
  base: '/aplication',
  routes,
  // base: process.env.BASE_URL,
})

router.beforeEach(async (to, from, next) => {
  if (to.name !== 'login' && to.name !== 'logout') {

    //store.commit('setTemplateRendered', false)
    await store.dispatch('msal/profileCheck')

    const authenticationRequired = router.options.routes
                                    .find(r => r.name === to.name)
                                    ?.authenticationRequired

    if (!store.getters['msal/userProfile'].authenticated) {
      next({ name: 'login', params: { redirectPath: to.path} })
    } else if (authenticationRequired && !store.getters['msal/userProfile'].authenticated) {
      let snackDelay;
      if (from.name === 'Home') {
        snackDelay = 0
        //store.commit('setTemplateRendered', true)
        next(false)
      } else {
        snackDelay = 500
        next({ name: 'Home' })
      }
      store.dispatch('setSnack', {
        delay: snackDelay,
        type: 'error',
        text: 'Sem acesso.',
        showContact: true
      })
    } else {
      next()
    }
    
  } else {
    next()
  }

})
router.afterEach((to, from) => {
  Vue.nextTick(() => {
      document.title = `${DEFAULT_TITLE}: ${to.name}`
  })
})

export default router
