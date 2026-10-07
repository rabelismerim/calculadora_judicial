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
  const needAuthenticated = to.meta?.authenticated
  const neededPermissions = to.meta?.permissions as string[] || []
  const user = JSON.parse(sessionStorage.getItem('calculadora-user') || '{}')

  const { isActive, permissions: userPermissions } = user
  const hasAllPermissions = neededPermissions.every((permission: string) => userPermissions.includes(permission))

  if (
    (!needAuthenticated && neededPermissions.length === 0)
    || (needAuthenticated && isActive)
    || (neededPermissions.length > 0 && isActive && hasAllPermissions)
  ) {
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
