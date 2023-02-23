const getCalculation = () => api
  .get('/v1/calculation/')
  .then(({ data }) => data)

export default {
  getCalculation,
}
