const getCreditors = () => api
  .get('/v1/creditors/budgets/')
  .then(({ data }) => data)

const getCreditorsBudgets = () => api
  .get('/v1/creditors/budgets/')
  .then(({ data }) => data)

const getCreditorsNotice = () => api
  .get('/v1/creditors/notice/')
  .then(({ data }) => data)

const getCreditorsClasses = () => api
  .get('/v1/creditors/classes/')
  .then(({ data }) => data)

export default {
  getCreditors,
  getCreditorsBudgets,
  getCreditorsNotice,
  getCreditorsClasses,
}
