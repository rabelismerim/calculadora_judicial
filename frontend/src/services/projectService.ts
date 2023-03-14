import { formatDateBackend } from '../composables/utils'

const mapProject = ({
  id,
  description,
  created_at,
  is_adm,
  status_display,
  process_number,
  engagement,
  process_start,
  process_end,
  calculation_manager,
  financial_manager,
  legal_manager,
  financial_partner,
  legal_partner,
  judge,
  lawyer,
  region,
  court,
}: any) => ({
  id,
  name: description,
  createdAt: formatDate(created_at),
  fase: is_adm ? 'Administrativa' : 'Judicial',
  status: status_display,
  processNumber: process_number,
  responsible: engagement?.create_user,
  engagements: engagement.numbers,
  start: process_start,
  end: process_end,
  calculationManager: calculation_manager,
  financialManager: financial_manager,
  legalManager: legal_manager,
  financialPartner: financial_partner,
  legalPartner: legal_partner,
  judge,
  lawyer,
  region,
  court,
})
const getProjects = () => api
  .get('/v1/projects/')
  .then(({ data }) => data.projects.map(mapProject))
const getProject = (id: string) => api
  .get(`/v1/projects/${id}/`)
  .then(({ data }) => data.project)
  .then(mapProject)
const newProject = ({
  judgeId,
  lawyerId,
  regionId,
  courtId,
  description,
  processNumber,
  start,
  end,
  legalManagerId,
  legalPartnerId,
  financialManagerId,
  financialPartnerId,
  calculationManagerId,
  engagements,
  recoverings,
  executors,
  approvers,
  reviewers,
}: any) => api
  .post('v1/projects/', {
    judge_id: judgeId,
    lawyer_id: lawyerId,
    region_id: regionId,
    court_id: courtId,
    description,
    process_number: processNumber,
    project_start: start && formatDateBackend(start),
    project_end: end && formatDateBackend(end),
    legal_manager_id: legalManagerId,
    legal_partner_id: legalPartnerId,
    financial_manager_id: financialManagerId,
    financial_partner_id: financialPartnerId,
    calculation_manager_id: calculationManagerId,
    engagement: {
      numbers: engagements,
    },
    recoverings: recoverings.map(({ name, legalNumber }: any) => ({
      entity: {
        name,
        legal_number: legalNumber,
      },
    })),
    executors: executors.map((id: string) => ({ id })),
    approvers: approvers.map((id: string) => ({ id })),
    reviewers: reviewers.map((id: string) => ({ id })),
  })

// JUDGES
const getJudges = () => api
  .get('/v1/projects/judge/')
  .then(({ data }) => data.judges)
  .then(data => data.map(({ description, id }: any) => ({ description, id })))
const newJudge = (description: string) => api
  .post('/v1/projects/judge/', { description })
  .then(({ data }) => data.judges)
  .then(({ description, id }) => ({ description, id }))

// LAWYERS
const getLawyers = () => api
  .get('/v1/projects/lawyer/')
  .then(({ data }) => data.lawyers)

// REGIONS
const getRegions = () => api
  .get('/v1/projects/region/')
  .then(({ data }) => data.regions)
  .then(data => data.map(({ description, id }: any) => ({ description, id })))
const newRegion = (description: string) => api
  .post('/v1/projects/region/', { description })
  .then(({ data }) => data.regions)
  .then(({ description, id }) => ({ description, id }))

// COURTS
const getCourts = () => api
  .get('/v1/projects/court/')
  .then(({ data }) => data.courts)
  .then(data => data.map(({ description, id }: any) => ({ description, id })))
const newCourt = (description: string) => api
  .post('/v1/projects/court/', { description })
  .then(({ data }) => data.courts)
  .then(({ description, id }) => ({ description, id }))

// ENGAGEMENTS OF PROJECT
const getEngagements = () => api
  .get('/v1/projects/engagement/')
  .then(({ data }) => data)

// USER OF PROJECT
const getUsers = () => api
  .get('/v1/projects/project_user/')
  .then(({ data }) => data)

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
