const userFallback = {
  authenticated: false,
  authorized: false,
  user_fullname: '',
  user_picture: '',
}
const store = useStorage('deloitte-user', { ...userFallback }, sessionStorage)

const login = async () => {
  try {
    const user = await usersService.getMyProfile()
    store.value = user

    return user.authenticated
  }
  catch (error) {
    console.warn('ERROR ON LOGIN:', error)
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
