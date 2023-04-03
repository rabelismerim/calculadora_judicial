const getPermissions = () => api
  .get('/user/detail/')
  .then(({ user }: any) => user)
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
  .then(({ users }: any) => users.map((user: any) => ({
    ...user,
    picture: user.userpicture,
  })))

const getGroups = () => api
  .get('/groups/')
  .then(({ groups }: any) => groups)

const requestAccess = (email: string) => api
  .post('/user/sendmail/', { email })

const setPermission = ({ email, groups }: any) => api
  .post('user/authorize/', { email, groups })

export default {
  getMyProfile,
  getPermissions,
  getGroups,
  getUsers,
  requestAccess,
  setPermission,
}
