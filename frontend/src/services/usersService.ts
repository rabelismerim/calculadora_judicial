const getPermissions = () => api
  .get('/user/detail/')
  .then(({ data }) => data.user)
  .then(({
    is_active,
    is_staff,
    groups,
    email,
    full_name,
    user_permissions,
    userpicture,
  }) => ({
    name: full_name,
    isActive: is_active,
    groups,
    email,
    isStaff: is_staff,
    picture: userpicture,
    permissions: user_permissions.map(({ codename }: any) => codename),
  }))

const getMyProfile = () => api
  .get('/drfmsal_signstatus/')
  .then(({ data }) => data.profile)
  .then(({
    authenticated,
    authorized,
    user_fullname,
    user_picture,
  }) => ({
    authenticated,
    authorized,
    name: user_fullname,
    picture: user_picture,
  }))
  .then(async (user) => {
    if (!user.authenticated && import.meta.env.PROD)
      redirectTo(`${window.location.origin}/djud/api/drfmsal_signin/djud/`)

    const permissions = await getPermissions()

    return {
      ...user,
      ...permissions,
    }
  })

const getUsers = () => api
  .get('/users/')
  .then(({ data }) => data.users.map(({
    id,
    first_name,
    last_name,
    email,
    groups,
    is_active,
    is_staff,
  }: any) => ({
    id,
    name: `${first_name} ${last_name}`,
    email,
    isActive: is_active,
    isStaff: is_staff,
    groups,
  })))

const getGroups = () => api
  .get('/groups/')
  .then(({ data }) => data.groups.map(({
    id,
    name,
  }: any) => ({
    id,
    name,
  })))

const requestAccess = (email: string) => api
  .post('/user/sendmail/', { email })
  // .then(({ data }) => data)

export default {
  getMyProfile,
  getPermissions,
  getGroups,
  getUsers,
  requestAccess,
}
