const verifyUser = () => api
  .get('/drfmsal_signstatus/')
  .then((result: any) => result?.profile)

const getPermissions = () => api
  .get('/user/detail/')
  .then((result: any) => result?.user || {})
  .then((user: any = {}) => {
    const {
      userPermissions: permissions,
    } = user
    return {
      ...user,
      permissions: permissions ? permissions.map(({ codename }: any) => codename) : [],
    }
  })

const logout = () => api
  .post('/v1/logout/')

const getMyProfile = async () => verifyUser()
  .then(async (user: any = {}) => {
    const goToSignin = () =>
      redirectTo(`${window.location.origin}/juca/api/drfmsal_signin/juca/`)

    const { authenticated, authorized, isActive } = user

    const inProduction = import.meta.env.PROD
    const inDevelopment = import.meta.env.DEV

    if ((!authenticated && inProduction)
      || (authenticated && isActive && !authorized && inProduction))
      goToSignin()

    const permissions = (authorized || inDevelopment) ? await getPermissions() : []
    const projects = (authorized || inDevelopment) ? await projectService.getUserProjects() : []

    return {
      ...user,
      ...permissions,
      projects,
    }
  })

const getUsers = () => api
  .get('/users/')
  .then((result: any) => result?.users || [])
  .then((users: any[]) => users?.filter(({ role }: any) => !['R'].includes(role)))

const getGroups = () => api
  .get('/groups/')
  .then((result: any) => result?.groups
    ?.map(({ name: description, id }: any) => ({ id, description })))

const sendmail = (email: string) => api
  .post('/user/sendmail/', { email })

const setPermission = ({ email, groups, role, status }: any) => api
  .post('user/authorize/', { email, groups, role, status, isActive: status === 'A' })
  .then((result: any) => result?.user)

const getEmailManagers = () => api
  .get('/emails/')
  .then((result: any) => result?.users
    ?.map(({ email }: any) => email))

export default {
  getMyProfile,
  getPermissions,
  getGroups,
  getUsers,
  sendmail,
  getEmailManagers,
  setPermission,
  verifyUser,
  logout,
}
