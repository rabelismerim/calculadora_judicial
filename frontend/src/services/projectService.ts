// BIG NUMBERS
import { formatDay, formatMonth } from '../composables/utils'

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
      user,
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
    const { projectUsers = [], recoverings = [] } = project

    project.recoverings = recoverings?.map((recovering: any) => ({
      ...recovering,
      creditors: recovering.creditors?.map((creditor: any) => ({ ...creditor, isValidating: false })),
    }))

    const participants = projectUsers.reduce((acc: any, current: any) => {
      const { id, idUser, firstName, lastName, username, pictureUrl, groups } = current
      const user = {
        id: idUser,
        idUser: id,
        pictureUrl,
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
    project.participants = [
      ['Executor', participants.Executor],
      ['Revisor', participants.Revisor],
      ['Aprovador', participants.Aprovador],
      ['Aprovador Especial', participants['Aprovador Especial']],
    ]
    const mapId = ({ id }: any) => (`${id}`)
    project.executors = participants.Executor?.map(mapId)
    project.reviewers = participants.Revisor?.map(mapId)
    project.approvers = participants.Aprovador?.map(mapId)
    project.specialApprovers = participants['Aprovador Especial']?.map(mapId)
    return project
  })

const mapId = (id: number) => ({ id })
const newProject = (project: any) => {
  const { executors, reviewers, approvers, specialApprovers, engagements, recoverings } = project
  const data = {
    ...project,
    engagement: {
      numbers: engagements,
    },
    recoverings: recoverings?.map((recovering: any) => ({
      entity: recovering,
    })),
    executors: executors?.map(mapId),
    approvers: approvers?.map(mapId),
    reviewers: reviewers?.map(mapId),
    specialApprovers: specialApprovers?.map(mapId),
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
  specialApprovers,
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
    executors: executors?.map(mapId),
    approvers: approvers?.map(mapId),
    reviewers: reviewers?.map(mapId),
    specialApprovers: specialApprovers?.map(mapId),
  })
  .then((result: any) => result?.project)

// JUDGES
const getJudges = () => api
  .get('/v1/projects/judge/')
  .then((result: any) => result?.judges || [])
  .then(data => data?.map(({ description, id }: any) => ({ description, id })))
const newJudge = (description: string) => api
  .post('/v1/projects/judge/', { description })
  .then((result: any) => result?.judge || {})
  .then(({ description, id }) => ({ description, id }))

// LAWYERS
const getLawyers = () => api
  .get('/v1/projects/lawyer/')
  .then((result: any) => result?.lawyers)
  .then(data => data?.map(({ description, id }: any) => ({ description, id })))
const newLawyer = (description: string) => api
  .post('/v1/projects/lawyer/', { description })
  .then((result: any) => result?.lawyer || {})
  .then(({ description, id }) => ({ description, id }))

// REGIONS
const getRegions = () => api
  .get('/v1/projects/region/')
  .then((result: any) => result?.regions)
  .then(data => data?.map(({ description, id }: any) => ({ description, id })))
const newRegion = (description: string) => api
  .post('/v1/projects/region/', { description })
  .then((result: any) => result?.region || {})
  .then(({ description, id }) => ({ description, id }))

// COURTS
const getCourts = () => api
  .get('/v1/projects/court/')
  .then((result: any) => result?.courts)
  .then(data => data?.map(({ description, id }: any) => ({ description, id })))
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

// BIG NUMBERS
const getDashboardBigNumbers = () => api
  .get('/v1/big_number/dashboard/')
  .then((data: any) => ({
    rangeDays: data?.rangeForDays?.map(({ day, total }: any) => [formatDay(day), total]) || [],
    rangeMonths: data?.rangeForMonth?.map(({ month, total }: any) => [formatMonth(month), total]) || [],
    byPhase: [
      {
        color: '#86BC25',
        count: data?.byPhase.adm || 0,
        label: 'Administrativa',
      },
      {
        color: '#000000',
        count: data?.byPhase.judicial || 0,
        label: 'Judicial',
      },
    ],
  }))
const stepColors: any = {
  S: '#AAAAAA', // To Calculate
  C: '#C4D600', // To Review
  E: '#86BC25', // To Approve
  B: '#43B02A', // To Approve Special
  A: '#007CB0', // Approved
  R: '#DA291C', // Failed
}
const getProjectBigNumbers = (projectId: string) => api
  .get(`/v1/big_number/project/${projectId}/`)
  .then((data: any) => ({
    ...data,
    byStep: data?.byStep?.map(({ total, step, stepDisplay }: any) => ({
      color: stepColors[step],
      count: total,
      label: stepDisplay,
    })) || [],
    classesCalculationsCount: data?.totalClassesCreditor?.map(({ classesDisplay, quantity }: any) => ({
      label: classesDisplay.split(' - ')?.[0] || '',
      count: quantity,
    })),
    classesCalculationsTotal: data?.totalClassesCreditor?.map(({ classesDisplay, totalHistorical, totalCalculated }: any) => ({
      label: classesDisplay.split(' - ')?.[0] || '',
      calc: totalCalculated / 1000,
      calcHint: formatNumber(totalCalculated, 2),
      hist: totalHistorical / 1000,
      histHint: formatNumber(totalHistorical, 2),
      digits: 2,
    })),
  }))
const getCreditorBigNumbers = (creditorId: string) => api
  .get(`/v1/big_number/creditor/${creditorId}/`)
  .then((data: any) => data?.total)

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
  getDashboardBigNumbers,
  getProjectBigNumbers,
  getCreditorBigNumbers,
}
