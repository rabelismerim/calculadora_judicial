const userFallback = {
  authenticated: undefined,
  authorized: undefined,
  fullName: undefined,
  picture: undefined,
}

const store = useStorage('deloitte-user', { ...userFallback }, sessionStorage)

const login = async () => {
  const router = useRouter()
  try {
    const user = await usersService.getMyProfile()
    store.value = user

    if (!user.authenticated && import.meta.env.PROD)
      redirectTo(`${window.location.origin}/djud/api/drfmsal_signin/djud/`)

    return user.authenticated
  }
  catch (error: any) {
    throwError(error)
    console.warn('ERROR ON LOGIN:', error)
    router.push({ path: '/' })
  }
}
const logout = () => {
  store.value = { ...userFallback }
}
const getUser = computed(() => store)
const isAuthenticated = computed(() => store.value.authenticated)
const hasPermission = computed(() => store.value.authorized)

export default {
  login,
  logout,
  getUser,
  isAuthenticated,
  hasPermission,
}
