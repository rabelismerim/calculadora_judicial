const userFallback = {
  authorized: null,
  isActive: null,
  name: '',
  fullName: '',
  pictureUrl: '',
  userpicture: '',
  email: '',
  groups: [] as any[],
  permissions: [] as string[],
  projects: [] as string[],
}

const store = useStorage('deloitte-user', clone(userFallback), sessionStorage)

const login = async () => {
  try {
    const user = await usersService.getMyProfile()

    printError('ON LOGIN SUCCESS:', user)
    store.value = {
      ...store.value,
      ...user,
    }
    return user
  }
  catch (error: any) {
    printError('ERROR ON LOGIN:', error)
    router?.push({ path: '/' })
  }
}
const logout = async () => {
  store.value = clone(userFallback)
  await delay(2)
  deleteAllCookies()
}
const user = computed(() => store.value)
const isActive = computed(() => store.value.isActive)
const hasPermissions = (...permissions: string[]) => permissions
  .every(permission => store.value.permissions.includes(permission))
const hasProject = (id: string) => store.value.projects.includes(id)

export default {
  login,
  logout,
  user,
  isActive,
  hasPermissions,
  hasProject,
}
