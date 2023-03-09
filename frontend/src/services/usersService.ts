const getPermissions = () => api
  .get('/user/detail/')
  .then(({ data }) => data.user)
  .then(({
    is_active,
    groups,
    user_permissions,
  }) => ({
    isActive: is_active,
    groups,
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

export default {
  getMyProfile,
  getPermissions,
  getGroups,
  getUsers,
}
