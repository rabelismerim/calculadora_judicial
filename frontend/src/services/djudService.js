import axios from "../plugins/axios"


const getDjudUsers = () => axios
    .get(`${baseUrl}/djud/api/v1/users/`)
    .then(({data}) => data)

const getDjudMsal = () => axios
    .get(`${baseUrl}/djud/api/drfmsal_signstatus`)
    .then(({data}) => data)


export default {
    getDjudUsers,
    getDjudMsal,
} 