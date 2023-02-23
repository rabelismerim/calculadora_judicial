const getProjects = () => api
  .get('/v1/projects/')
  .then(({ data }) => data)

const getProjectJudge = () => api
  .get('/v1/projects/judge/')
  .then(({ data }) => data)

const getProjectLawyer = () => api
  .get('/v1/projects/lawyer/')
  .then(({ data }) => data)

const getProjectRegion = () => api
  .get('/v1/projects/region/')
  .then(({ data }) => data)

const getProjectEngagement = () => api
  .get('/v1/projects/engagement/')
  .then(({ data }) => data)

const getProjectUser = () => api
  .get('/v1/projects/project_user/')
  .then(({ data }) => data)

export default {
  getProjects,
  getProjectJudge,
  getProjectLawyer,
  getProjectRegion,
  getProjectEngagement,
  getProjectUser,
}
