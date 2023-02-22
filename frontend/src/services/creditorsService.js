import axios from "../plugins/axios"


const getCreditors = () => axios
    .get(`/v1/creditors/budgets`)
    .then(({data}) => data)

const getCreditorsBudgets = () => axios
    .get(`/v1/creditors/budgets`)
    .then(({data}) => data)

const getCreditorsNotice = () => axios
    .get(`/v1/creditors/notice`)
    .then(({data}) => data)

const getCreditorsClasses = () => axios
    .get(`/v1/creditors/classes`)
    .then(({data}) => data)


export default {
  getCreditors,
  getCreditorsBudgets,
  getCreditorsNotice,
  getCreditorsClasses,

} 