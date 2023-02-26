const getBaseCoins = () => api
  .get('/v1/base/coins/')
  .then(({ data }) => data)

export default {
  getBaseCoins,
}
