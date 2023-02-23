const login = () => api
  .get('/drfmsal_signin/djud/')

const getMyProfile = () => api
  .get('/drfmsal_signstatus')
  .then(({ data }) => data.profile)

const getUsers = () => api
  .get('/v1/users/')
  .then(({ data }) => data)

export default {
  getMyProfile,
  getUsers,
  login,
}
