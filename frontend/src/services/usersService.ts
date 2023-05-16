const getPermissions = () => api
  .get('/user/detail/')
  .then((result: any) => result?.user || {})
  .then((user: any = {}) => {
    const {
      userpicture: picture,
      userPermissions: permissions,
    } = user
    return {
      ...user,
      picture,
      permissions: permissions ? permissions.map(({ codename }: any) => codename) : [],
    }
  })

const getMyProfile = () => api
  .get('/drfmsal_signstatus/')
  .then(({ profile }: any) => profile)
  .then(async (user) => {
    if (!user.authenticated && import.meta.env.PROD)
      redirectTo(`${window.location.origin}/djud/api/drfmsal_signin/djud/`)

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
  .then((result: any) => result?.users?.map((user: any) => ({
    ...user,
    picture: user.userpicture,
  })) || [])

const getGroups = () => api
  .get('/groups/')
  .then((result: any) => result?.groups
    ?.map(({ name: description, id }: any) => ({ id, description })))

const requestAccess = (email: string) => api
  .post('/user/sendmail/', { email })

const setPermission = ({ email, groups, role, isActive }: any) => api
  .post('user/authorize/', { email, groups, role, isActive })

export default {
  getMyProfile,
  getPermissions,
  getGroups,
  getUsers,
  requestAccess,
  setPermission,
}
