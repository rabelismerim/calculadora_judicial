// CREDORES
interface Claim {
  classe: string
  coin: string
  value: number
}
interface Creditor {
  id?: string
  name: string
  legalNumber: string
  recoveringsId: string[]
  rateId: string
  claimCreditor: Claim[]
  admission: string
  dismissal: string
  defaultInterest: number
  fine: number
  advocativeHours: number
  occurrence: string
  physicalPerson: boolean
  description: string
  recoverings?: { recoveringId: string; rateId: string }[]
}

const getCreditors = (projectId: string, pagination = {}) => api
  .get(`/v1/creditors/project/${projectId}/${controlPagination(pagination)}`)
  .then(result => ({ items: result?.data?.results, count: result?.data.count }))
const getCreditorsByLegalNumber = (legalNumber: string, pagination: any) => api
  .get(`/v1/creditors/recovering_legal_number/${legalNumber}/${controlPagination(pagination)}`)
  .then((result: any) => ({ items: result?.data?.results, count: result?.data?.count }))

const getInactiveCreditors = (projectId: string) => api
  .get(`/v1/creditors/project/inactive/${projectId}/`)
  .then((result: any) => result?.creditors)

const getCreditor = (creditorId: string) => api
  .get(`/v1/creditors/detail/${creditorId}/`)

const getOptions = () => api
  .get('/v1/creditors/options/')
  .then((result: any) => result?.options)

const newCreditors = async (creditor: Creditor) => {
  const { recoverings, name, legalNumber } = creditor
  const results = []
  if (!recoverings)
    return
  try {
    for (const recoveringId of recoverings) {
      const result = await api.post('/v1/creditors/',
        ({
          ...creditor,
          entity: {
            name,
            legalNumber,
          },
          recoveringId,
        }))
        .then((result: any) => result?.creditor)
      results.push(result)
    }
    return results
  }
  catch (error) {
    printError('ERROR ON NEW CREDITORS', error)
  }
}
const updateCreditor = async (creditor: any) => api
  .put(`/v1/creditors/${creditor.id}/`, creditor)
  .then((result: any) => result?.creditor)

interface Notice {
  id?: string
  creditorId: string
}

const getNoticeAJ = () => api
  .get('/v1/creditors/notice/aj/')
  .then((result: any) => result?.notices)

const getNoticeAJCreditor = (creditorId: any) => api
  .get(`/v1/creditors/notice/aj/creditor/${creditorId}/`)
  .then((result: any) => result?.notices ?? [])

const getNoticeAJRecovering = (creditorId: any) => api
  .get(`/v1/creditors/notice/recovering/creditor/${creditorId}/`)
  .then((result: any) => result?.noticeRecoverings ?? [])

const setNoticeAJ = async (notice: Notice) => {
  const { id } = notice
  const method = id ? 'put' : 'post'
  return api[method](`/v1/creditors/notice/aj/${id ? `${id}/` : ''}`, notice)
}

const getNoticeRecovering = () => api
  .get('/v1/creditors/notice/recovering/')
  .then((result: any) => result?.noticeRecoverings)
const setNoticeRecovering = async (notice: Notice) => {
  const { id } = notice
  const method = id ? 'put' : 'post'
  return api[method](`/v1/creditors/notice/recovering/${id ? `${id}/` : ''}`, notice)
}

const getCreditorClaims = (creditorId: string) => api
  .get(`/v1/base/claim-creditor/creditor/${creditorId}/`)
const setCreditorClaim = async (notice: Notice) => {
  const { id } = notice
  const method = id ? 'put' : 'post'
  return api[method](`/v1/base/claim-creditor/${id ? `${id}/` : ''}`, notice)
}

const setLawyerClaim = async (notice: Notice) => api
  .post('/v1/base/claim-lawyer/', notice)

const validateCalculations = async (creditorId: string, calculationIds: string[]) => api
  .post(`/v1/creditors/${creditorId}/validate/`, {
    calculations: calculationIds.map((id: string) => ({ id })),
  })

export default {
  getCreditors,
  getCreditorsByLegalNumber,
  getInactiveCreditors,
  getCreditor,
  updateCreditor,
  getOptions,
  newCreditors,
  getNoticeAJ,
  getNoticeAJCreditor,
  getNoticeAJRecovering,
  setNoticeAJ,
  getNoticeRecovering,
  setNoticeRecovering,
  getCreditorClaims,
  setCreditorClaim,
  setLawyerClaim,
  validateCalculations,
}
