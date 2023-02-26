const login = () => api
  .get('/drfmsal_signin/djud/')

const getMyProfile = () => api
  .get('/drfmsal_signstatus')
  .then(({ data }) => data.profile)
  .then(({
    authenticated,
    authorized,
    user_fullname,
    user_picture,
  }) => ({
    authenticated,
    authorized,
    fullName: user_fullname,
    picture: user_picture,
  }))

const getUsers = () => api
  .get('/v1/users/')
  .then(({ data }) => data)

export default {
  getMyProfile,
  getUsers,
  login,
}
