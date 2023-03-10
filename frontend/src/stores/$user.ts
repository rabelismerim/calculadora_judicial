const userFallback = {
  isActive: null,
  name: '',
  picture: '',
  email: '',
  groups: [] as any[],
  permissions: [] as string[],
}

const store = useStorage('deloitte-user', { ...userFallback }, sessionStorage)

const login = async () => {
  const router = useRouter()
  try {
    const user = await usersService.getMyProfile()
    store.value = {
      ...store.value,
      ...user,
    }

    return user.authorized
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
const user = computed(() => store.value)
const isActive = computed(() => store.value.isActive)
const hasPermissions = (permissions: string[] = []) => permissions
  .every(permission => store.value.permissions.includes(permission))

export default {
  login,
  logout,
  user,
  isActive,
  hasPermissions,
}
