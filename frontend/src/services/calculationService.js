import axios from "../plugins/axios"


const getCalculation = () => axios
    .get(`/v1/calculation/`)
    .then(({data}) => data)

export default {
    getCalculation,
} 