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

const setCreditor = async (creditor: Creditor) => {
  const { id, recoveringsId, name, legalNumber, claimCreditor } = creditor
  const method = id ? 'put' : 'post'
  const results = []
  if (!recoveringsId)
    return
  try {
    for (const id of recoveringsId) {
      const result = await api[method]('/v1/creditors/',
        ({
          ...creditor,
          entity: {
            name,
            legalNumber,
          },
          recoveringId: id,
          claimCreditor: claimCreditor.map(({ coin, classe, value }: Claim) => ({
            classes: { classe },
            coins: { coin, value },
          })),
        }))
      // .then((result: any) => result.creditor)
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
  classe: string
  coin: string
  value: number
  creditorId: string
}
interface Recovering extends Notice {}

const getNoticeAJ = () => api
  .get('/v1/creditors/notice/aj/')
  .then((result: any) => result?.notices)

const setNoticeAJ = async (notice: Notice) => {
  const { id, classe, coin, creditorId, value } = notice
  const method = id ? 'put' : 'post'
  const results = []
  try {
    for (const id of creditorId) {
      const result = await api[method]('/v1/creditors/notice/aj/',
        ({
          ...notice,
          classes: {
            classe,
          },

          coins: {
            coin,
            value,
          },
          creditorId: id,
        }))
      results.push(result)
    }
    return results
  }
  catch (error) {
    printError('ERROR ON NEW NOTICE', error)
  }
}

const getNoticeRecovering = () => api
  .get('/v1/creditors/notice/recovering/')
  .then((result: any) => result?.noticeRecoverings)

const setNoticeRecovering = async (recovering: Recovering) => {
  const { id, classe, coin, creditorId, value } = recovering
  const method = id ? 'put' : 'post'
  const results = []
  try {
    for (const id of creditorId) {
      const result = await api[method]('/v1/creditors/notice/recovering/',
        ({
          ...recovering,
          classes: {
            classe,
          },

          coins: {
            coin,
            value,
          },
          creditorId: id,
        }))
        .then((result: any) => result.recovering)
      results.push(result)
    }
    return results
  }
  catch (error) {
    printError('ERROR ON NEW RECOVERING', error)
  }
}

export default {
  getCreditors,
  getCreditor,
  getOptions,
  setCreditor,
  getNoticeAJ,
  setNoticeAJ,
  getNoticeRecovering,
  setNoticeRecovering,
}
