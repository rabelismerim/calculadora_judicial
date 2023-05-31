const mapProject = (project: any) => {
  const {
    isAdm,
    engagement,
    financialPartner,
    financialManager,
    legalPartner,
    legalManager,
    calculationManager,
  } = project

  const responsibles = [
    { role: 'Sócio Financeiro', user: financialPartner },
    { role: 'Sócio Jurídico', user: legalPartner },
    { role: 'Gerente Financeiro', user: financialManager },
    { role: 'Gerente Jurídico', user: legalManager },
    { role: 'Gerente de Cálculo', user: calculationManager },
  ]
    .filter(({ user }) => user)
    .map(({ user, role }) => ({
      role,
      user: {
        ...user,
        picture: user.userpicture,
      },
    }))

  return {
    ...project,
    fase: isAdm ? 'Administrativa' : 'Judicial',
    responsible: engagement?.createUser,
    responsibles,
  }
}
const getUserProjects = () => api
  .get('/v1/projects/project_user/')
  .then((result: any) => [...new Set(result?.projectUser || [])])
const getProjects = () => api
  .get('/v1/projects/')
  .then((result: any) => result?.projects?.map(mapProject) || [])
const getProject = (id: string) => api
  .get(`/v1/projects/${id}/`)
  .then((result: any) => result?.project)
  .then(mapProject)
  .then((project: any) => {
    const { projectUsers = [] } = project

    project.participants = projectUsers.reduce((acc: any, current: any) => {
      const { firstName, lastName, username, userpicture, groups } = current
      const user = {
        picture: userpicture,
        fullName: `${firstName} ${lastName}`,
        email: `${username}@deloitte.com`,
      }
      groups.forEach(({ name }: any) => {
        if (!acc[name])
          acc[name] = []
        acc[name].push(user)
      })
      return acc
    }, {})

    return project
  })

const mapId = (id: string) => ({ id })
const newProject = (project: any) => {
  const { executors, approvers, reviewers, engagements, recoverings } = project
  const data = {
    ...project,
    engagement: {
      numbers: engagements,
    },
    recoverings: recoverings.map((recovering: any) => ({
      entity: recovering,
    })),
    executors: executors.map(mapId),
    approvers: approvers.map(mapId),
    reviewers: reviewers.map(mapId),
  }
  return api
    .post('/v1/projects/', data)
    .then((result: any) => result?.project)
}

const updateProject = ({
  id,
  description,
  engagements,
  processNumber,
  dateRjRequest,
  dateRjFiling,
  dateCitation,
  projectStart,
  projectEnd,
  judgeId,
  lawyerId,
  regionId,
  courtId,
  financialPartnerId,
  legalPartnerId,
  financialManagerId,
  legalManagerId,
  calculationManagerId,
  executors,
  reviewers,
  approvers,
}: any) => api
  .put(`/v1/projects/${id}/`, {
    description,
    engagements,
    processNumber,
    dateRjRequest,
    dateRjFiling,
    dateCitation,
    projectStart,
    projectEnd,
    judgeId,
    lawyerId,
    regionId,
    courtId,
    financialPartnerId,
    legalPartnerId,
    financialManagerId,
    legalManagerId,
    calculationManagerId,
    executors: executors.map(mapId),
    approvers: approvers.map(mapId),
    reviewers: reviewers.map(mapId),
  })
  .then((result: any) => result?.project)

// JUDGES
const getJudges = () => api
  .get('/v1/projects/judge/')
  .then((result: any) => result?.judges || [])
  .then(data => data.map(({ description, id }: any) => ({ description, id })))
const newJudge = (description: string) => api
  .post('/v1/projects/judge/', { description })
  .then((result: any) => result?.judge || {})
  .then(({ description, id }) => ({ description, id }))

// LAWYERS
const getLawyers = () => api
  .get('/v1/projects/lawyer/')
  .then(({ lawyers }: any) => lawyers)
  .then(data => data.map(({ description, id }: any) => ({ description, id })))
const newLawyer = (description: string) => api
  .post('/v1/projects/lawyer/', { description })
  .then((result: any) => result?.lawyer || {})
  .then(({ description, id }) => ({ description, id }))

// REGIONS
const getRegions = () => api
  .get('/v1/projects/region/')
  .then(({ regions }: any) => regions)
  .then(data => data.map(({ description, id }: any) => ({ description, id })))
const newRegion = (description: string) => api
  .post('/v1/projects/region/', { description })
  .then((result: any) => result?.region || {})
  .then(({ description, id }) => ({ description, id }))

// COURTS
const getCourts = () => api
  .get('/v1/projects/court/')
  .then(({ courts }: any) => courts)
  .then(data => data.map(({ description, id }: any) => ({ description, id })))
const newCourt = (description: string) => api
  .post('/v1/projects/court/', { description })
  .then((result: any) => result?.court || {})
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
  newLawyer,
  getProjects,
  getProject,
  getUserProjects,
  newProject,
  updateProject,
  getCourts,
  newCourt,
  getRegions,
  newRegion,
  getUsers,
}
