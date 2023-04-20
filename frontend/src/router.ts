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
  const permissions = to.meta?.permissions as string[] || []
  const authenticated = to.meta?.authenticated
  const { permissions: userPermissions } = JSON.parse(sessionStorage.getItem('deloitte-user') || '{}')
  const hasAllPermissions = permissions.every((permission: string) => userPermissions.includes(permission))
  if ((!permissions && !authenticated) || hasAllPermissions) {
    next()
    return
  }

  throwError({
    message: 'Você não tem permissão de ver essa página!',
    id: 'UNAUTHORIZED',
  })
  next('/')
})

export default router
