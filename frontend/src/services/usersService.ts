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

const getMyProfile = () => api
  .get('/drfmsal_signstatus/')
  .then((result: any) => result?.profile)
  .then(async (user) => {
    if (!user?.authenticated && import.meta.env.PROD)
      redirectTo(`${window.location.origin}/juca/api/drfmsal_signin/juca/`)

    const permissions = await getPermissions()
    const projects = await projectService.getUserProjects()

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
  .post('user/authorize/', { email, groups, role, status })
  .then((result: any) => result?.user)

export default {
  getMyProfile,
  getPermissions,
  getGroups,
  getUsers,
  sendmail,
  setPermission,
}
