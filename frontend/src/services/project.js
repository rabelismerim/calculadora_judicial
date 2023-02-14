import axios from "../plugins/axios"


const getProjects = () => axios
    .get(`${baseUrl}/djud/api/v1/projects`)
    .then(({data}) => data)

const getProjectJudge = () => axios
    .get(`${baseUrl}/djud/api/v1/projects/judge`)
    .then(({data}) => data)

const getProjectLawyer = () => axios
    .get(`${baseUrl}/djud/api/v1/projects/lawyer`)
    .then(({data}) => data)

const getProjectRegion = () => axios
    .get(`${baseUrl}/djud/api/v1/projects/region`)
    .then(({data}) => data)

const getProjectEngagement = () => axios
    .get(`${baseUrl}/djud/api/v1/projects/engagement`)
    .then(({data}) => data)

const getProjectUser = () => axios
    .get(`${baseUrl}/djud/api/v1/projects/project_user`)
    .then(({data}) => data)


export default {
    getProjects,
    getProjectJudge, 
    getProjectLawyer,
    getProjectRegion, 
    getProjectEngagement,
    getProjectUser, 
} 