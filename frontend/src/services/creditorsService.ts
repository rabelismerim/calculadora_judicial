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
interface Detail extends Creditor {}
interface Options extends Creditor {
  legend: string
}
const getCreditors = (id: string) => api
  .get(`/v1/creditors/project/${id}/`)
  .then((result: any) => result?.creditors)

const getCreditor = (id: string) => api
  .get(`/v1/creditors/detail/${id}/`)
  .then((result: any) => result?.creditor)

const getOptions = () => api
  .get('/v1/creditors/options/')
  .then((result: any) => result?.options)

const newCreditors = async (creditor: Creditor) => {
  const { recoverings, name, legalNumber } = creditor
  const results = []
  if (!recoverings)
    return
  try {
    for (const { recoveringId, rateId } of recoverings) {
      const result = await api.post('/v1/creditors/',
        ({
          ...creditor,
          entity: {
            name,
            legalNumber,
          },
          recoveringId,
          rateId,
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

interface Notice {
  id?: string
  creditorId: string
}

const getNoticeAJ = () => api
  .get('/v1/creditors/notice/aj/')
  .then((result: any) => result?.notices)
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

const setCreditorClaim = async (notice: Notice) => {
  const { id } = notice
  const method = id ? 'put' : 'post'
  return api[method](`/v1/claim/claim/claim-creditor/${id ? `${id}/` : ''}`, notice)
}
const setLawyerClaim = async (notice: Notice) => {
  const { id } = notice
  const method = id ? 'put' : 'post'
  return api[method](`/v1/claim/claim/claim-lawyer/${id ? `${id}/` : ''}`, notice)
}

export default {
  getCreditors,
  getCreditor,
  getOptions,
  newCreditors,
  getNoticeAJ,
  setNoticeAJ,
  getNoticeRecovering,
  setNoticeRecovering,
  setCreditorClaim,
  setLawyerClaim,
}
