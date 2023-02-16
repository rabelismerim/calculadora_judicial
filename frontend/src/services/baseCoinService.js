import axios from "../plugins/axios"


const getBaseCoins = () => axios
    .get(`/v1/base/coins`)
    .then(({data}) => data)

export default {
    getBaseCoins,
} 