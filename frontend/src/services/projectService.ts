import { formatDateBackend } from '../composables/utils'

const mapProject = (project: any) => {
  const { createdAt, isAdm, engagement } = project
  return {
    ...project,
    createdAt: formatDate(createdAt),
    fase: isAdm ? 'Administrativa' : 'Judicial',
    responsible: engagement?.createUser,
  }
}
const getProjects = () => api
  .get('/v1/projects/')
  .then(({ projects }: any) => projects.map(mapProject))
const getProject = (id: string) => api
  .get(`/v1/projects/${id}/`)
  .then(({ project }: any) => project)
  .then(mapProject)

const newProject = (project: any) => {
  const { projectStart, projectEnd, executors, approvers, reviewers, statusDisplay } = project
  const data = {
    ...project,
    projectStart: projectStart ? formatDateBackend(projectStart) : undefined,
    projectEnd: projectEnd ? formatDateBackend(projectEnd) : undefined,
    executors: executors.map((id: string) => ({ id })),
    approvers: approvers.map((id: string) => ({ id })),
    reviewers: reviewers.map((id: string) => ({ id })),
  }
  return api.post('v1/projects/', data)
}

// JUDGES
const getJudges = () => api
  .get('/v1/projects/judge/')
  .then(({ judges }: any) => judges)
  .then(data => data.map(({ description, id }: any) => ({ description, id })))
const newJudge = (description: string) => api
  .post('/v1/projects/judge/', { description })
  .then(({ judges }: any) => judges)
  .then(({ description, id }) => ({ description, id }))

// LAWYERS
const getLawyers = () => api
  .get('/v1/projects/lawyer/')
  .then(({ lawyers }: any) => lawyers)

// REGIONS
const getRegions = () => api
  .get('/v1/projects/region/')
  .then(({ regions }: any) => regions)
  .then(data => data.map(({ description, id }: any) => ({ description, id })))
const newRegion = (description: string) => api
  .post('/v1/projects/region/', { description })
  .then(({ regions }: any) => regions)
  .then(({ description, id }) => ({ description, id }))

// COURTS
const getCourts = () => api
  .get('/v1/projects/court/')
  .then(({ courts }: any) => courts)
  .then(data => data.map(({ description, id }: any) => ({ description, id })))
const newCourt = (description: string) => api
  .post('/v1/projects/court/', { description })
  .then(({ courts }: any) => courts)
  .then(({ description, id }) => ({ description, id }))

// ENGAGEMENTS OF PROJECT
const getEngagements = () => api
  .get('/v1/projects/engagement/')

// USER OF PROJECT
const getUsers = () => api
  .get('/v1/projects/project_user/')

export default {
  getEngagements,
  getJudges,
  newJudge,
  getLawyers,
  getProjects,
  getProject,
  newProject,
  getCourts,
  newCourt,
  getRegions,
  newRegion,
  getUsers,
}
