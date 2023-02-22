import axios from "../plugins/axios"


const getRecovering = () => axios
    .get(`/v1/recovering`)
    .then(({data}) => data)

const getRecoveringArchive = () => axios
    .get(`/v1/recovering/archive_recovering`)
    .then(({data}) => data)


export default {
    getRecovering,
    getRecoveringArchive,

} 