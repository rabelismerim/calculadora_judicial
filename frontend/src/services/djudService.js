import axios from "../plugins/axios"


const getUsers = () => axios
    .get(`/v1/users/`)
    .then(({data}) => data.data)

const getProfile = () => axios
    .get(`/drfmsal_signstatus`)
    .then(({data}) => data.profile)


export default {
    getUsers,
    getProfile,
} 