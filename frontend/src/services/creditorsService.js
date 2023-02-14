import axios from "../plugins/axios"


const getCreditors = () => axios
    .get(`${baseUrl}/djud/api/v1/creditors/budgets`)
    .then(({data}) => data)

const getCreditorsBudgets = () => axios
    .get(`${baseUrl}/djud/api/v1/creditors/budgets`)
    .then(({data}) => data)

const getCreditorsNotice = () => axios
    .get(`${baseUrl}/djud/api/v1/creditors/notice`)
    .then(({data}) => data)

const getCreditorsClasses = () => axios
    .get(`${baseUrl}/djud/api/v1/creditors/classes`)
    .then(({data}) => data)


export default {
  getCreditors,
  getCreditorsBudgets,
  getCreditorsNotice,
  getCreditorsClasses,

} 