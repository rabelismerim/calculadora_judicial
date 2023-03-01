import { createRouter, createWebHistory } from 'vue-router'
import { setupLayouts } from 'virtual:generated-layouts'

import generatedRoutes from '~pages'

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
  try {
    const { authenticated, authorized } = await usersService.getMyProfile()
    if (!authenticated)
      redirectTo(`${window.location.origin}/djud/api/drfmsal_signin/djud/`)
    if (authorized)
      next()
  }
  catch (error) {
    next('/')
  }
})

export default router
