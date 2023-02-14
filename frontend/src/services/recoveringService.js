import axios from "../plugins/axios"


const getRecovering = () => axios
    .get(`${baseUrl}/djud/api/v1/recovering`)
    .then(({data}) => data)

const getRecoveringArchive = () => axios
    .get(`${baseUrl}/djud/api/v1/recovering/archive_recovering`)
    .then(({data}) => data)


export default {
    getRecovering,
    getRecoveringArchive,

} 