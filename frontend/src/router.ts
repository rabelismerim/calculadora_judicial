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
  const permissions = to.meta.permissions as string[]
  const { permissions: userPermissions } = JSON.parse(sessionStorage.getItem('deloitte-user') || '{}')
  if (permissions.every((permission: string) => userPermissions.includes(permission)))
    next()

  next('/')
})

export default router
