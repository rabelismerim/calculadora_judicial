const mapProject = (project: any) => {
  const {
    createdAt,
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
    createdAt: formatDate(createdAt),
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

const newProject = (project: any) => {
  const { start, end, executors, approvers, reviewers, engagements, recoverings } = project
  const data = {
    ...project,
    projectStart: start ? formatDateToBackend(start) : undefined,
    projectEnd: end ? formatDateToBackend(end) : undefined,
    engagement: {
      numbers: engagements,
    },
    recoverings: recoverings.map((recovering: any) => ({
      entity: recovering,
    })),
    executors: executors.map((id: string) => ({ id })),
    approvers: approvers.map((id: string) => ({ id })),
    reviewers: reviewers.map((id: string) => ({ id })),
  }
  return api
    .post('v1/projects/', data)
    .then(({ project }: any) => project)
}

// JUDGES
const getJudges = () => api
  .get('/v1/projects/judge/')
  .then((result: any) => result?.judges || [])
  .then(data => data.map(({ description, id }: any) => ({ description, id })))
const newJudge = (description: string) => api
  .post('/v1/projects/judge/', { description })
  .then((result: any) => result?.judges || [])
  .then(({ description, id }) => ({ description, id }))

// LAWYERS
const getLawyers = () => api
  .get('/v1/projects/lawyer/')
  .then(({ lawyers }: any) => lawyers)
  .then(data => data.map(({ description, id }: any) => ({ description, id })))
const newLawyer = (description: string) => api
  .post('/v1/projects/lawyer/', { description })
  .then(({ lawyers }: any) => lawyers)
  .then(({ description, id }) => ({ description, id }))

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
  newLawyer,
  getProjects,
  getProject,
  getUserProjects,
  newProject,
  getCourts,
  newCourt,
  getRegions,
  newRegion,
  getUsers,
}
