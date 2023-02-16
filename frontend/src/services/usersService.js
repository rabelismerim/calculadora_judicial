import axios from "../plugins/axios"


const getUSers = () => axios
    .get(`/users`)
    .then(({data}) => data)


export default {
    getUsers,
} 