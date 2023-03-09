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
  if (!to.meta?.permissions) {
    next()
    return
  }
  try {
    const { authenticated, permissions: userPermissions } = await usersService.getMyProfile()
    if (!authenticated && import.meta.env.PROD)
      redirectTo(`${window.location.origin}/djud/api/drfmsal_signin/djud/`)
    const permissions = to.meta.permissions as string[]
    if (permissions.every((permission: string) => userPermissions.includes(permission)))
      next()
  }
  catch (error) {
    next('/')
  }
})

export default router
