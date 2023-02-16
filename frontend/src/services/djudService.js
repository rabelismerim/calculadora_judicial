import axios from "../plugins/axios"


const getDjudUsers = () => axios
    .get(`/v1/users/`)
    .then(({data}) => data)

const getDjudMsal = () => axios
    .get(`/drfmsal_signstatus`)
    // .then(({data}) => data)


export default {
    getDjudUsers,
    getDjudMsal,
} 