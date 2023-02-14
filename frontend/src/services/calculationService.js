import axios from "../plugins/axios"


const getCalculation = () => axios
    .get(`${baseUrl}/djud/api/v1/calculation/`)
    .then(({data}) => data)

export default {
    getCalculation,
} 