import axios from "../plugins/axios"


const getBaseCoins = () => axios
    .get(`${baseUrl}/djud/api/v1/base/coins`)
    .then(({data}) => data)

export default {
    getBaseCoins,
} 