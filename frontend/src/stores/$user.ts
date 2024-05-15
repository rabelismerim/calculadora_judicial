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
  try {
    await usersService.logout()
    await delay(2)
    store.value = clone(userFallback)
    deleteAllCookies()
  }
  catch (error) {
    printError('ERROR ON LOGOUT:', error)
  }
}

const user = computed(() => store.value)
const isActive = computed(() => store.value.isActive)
const isAuthorized = computed(() => store.value.isActive)
const hasPermissions = (...permissions: string[]) => permissions
  .every(permission => store.value.permissions.includes(permission))

const updateProjectList = async () => {
  store.value.projects = await projectService.getUserProjects()
}

export default {
  login,
  logout,
  user,
  isActive,
  isAuthorized,
  hasPermissions,
  updateProjectList,
}
