import axios from "../plugins/axios"


const getUSers = () => axios
    .get(`${baseUrl}/djud/api/users`)
    .then(({data}) => data)


export default {
    getUsers,
} 