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
  .get(`/v1/projects/${id}`)
  .then(({ data }) => data.project)
  .then(mapProject)

const getJudges = () => api
  .get('/v1/projects/judge/')
  .then(({ data }) => data)

const getLawyers = () => api
  .get('/v1/projects/lawyer/')
  .then(({ data }) => data)

const getRegions = () => api
  .get('/v1/projects/region/')
  .then(({ data }) => data)

const getCourts = () => api
  .get('/v1/projects/court/')
  .then(({ data }) => data)

const getEngagements = () => api
  .get('/v1/projects/engagement/')
  .then(({ data }) => data)

const getUsers = () => api
  .get('/v1/projects/project_user/')
  .then(({ data }) => data)

export default {
  getCourts,
  getEngagements,
  getJudges,
  getLawyers,
  getProjects,
  getProject,
  getRegions,
  getUsers,
}
