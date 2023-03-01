const getProjects = () => api
  .get('/v1/projects/')
  .then(({ data }) => data.projects.map(({
    id,
    description,
    created_at,
    engagement,
    is_adm,
    status_display,
  }: any) => ({
    id,
    name: description,
    createdAt: formatDate(created_at),
    responsible: engagement?.create_user,
    fase: is_adm ? 'Administrativa' : 'Judicial',
    status: status_display,
  })))

const getProject = (id: string) => api
  .get(`/v1/projects/${id}`)
  .then(({ data }) => data.project)
  // .then(({ data }) => data.projects.map(({
  //   id,
  //   description,
  //   created_at,
  //   engagement,
  //   is_adm,
  //   status_display,
  // }: any) => ({
  //   id,
  //   name: description,
  //   createdAt: formatDate(created_at),
  //   responsible: engagement?.create_user,
  //   fase: is_adm ? 'Administrativa' : 'Judicial',
  //   status: status_display,
  // })))

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
  getProject,
  getProjectJudge,
  getProjectLawyer,
  getProjectRegion,
  getProjectEngagement,
  getProjectUser,
}
