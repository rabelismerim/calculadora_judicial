const mapCreditor = (creditor: any) => {
}

const mapAnalysi = (notice: any) => {
  // const {
  //   rateId: '',
  //   classe: '1',
  //   coin: 'B',
  //   value: 1000,
  //   archiveJson: '',
  //   noticeRecovering: '',
  //   admission: '2023-04-11T12:30:01.459Z',
  //   dismissal: '2023-04-11T12:30:01.459Z',
  //   defaultInterest: '0',
  //   fine: '0',
  //   advocativeHours: '0',
  //   description: 'descriçao',
  //   classe,
  //   coin,
  //   value,
  //   recovering_id,
  // } = creditor
}
// CREDORES
interface Creditor {
  name: string
  legalNumber: string
  recoveringsId: string[]
}
const getCreditors = (id: string) => api
  .get(`/v1/creditors/project/${id}/`)
  .then(({ analysis }: any) => analysis)
const newCreditor = async (creditor: Creditor) => {
  const { recoveringsId, name, legalNumber } = creditor
  const results = []
  try {
    for (const id of recoveringsId) {
      const result = await api
        .post('/v1/creditors/',
          ({
            entity: {
              name,
              legalNumber,
            },
            recoveringId: id,
            rateId: 'eca8d781-548f-4893-ba00-41893e605936',
          }))
        .then((result: any) => result.creditor)
      results.push(result)
    }
    return results
  }
  catch (error) {
    printError('ERROR ON NEW CREDITORS', error)
  }
}

// FICHA DE ANALISE - EDITAL DA AJ

interface Analysis {
  classe: string[]
  coin: string[]
  recoveringsId: string[]
  value: number
}

const getAnalysis = () => api
  .get('/v1/creditors/notice/aj/')
  .then(({ analysis }: any) => analysis)
const newAnalysis = async (notice: Analysis) => {
  const { classe, coin, recoveringsId, value } = notice
  const results = []
  try {
    for (const id of recoveringsId) {
      const result = await api
        .post('/v1/creditors/notice/aj/',
          ({
            classes: {
              classe,
            },

            coins: {
              coin,
              value,
            },
            recoveringsId: id,
          }))
        .then((result: any) => result.notice)
      results.push(result)
    }
    return results
  }
  catch (error) {
    printError('ERROR ON NEW ANALYSIS', error)
  }
}

// FICHA DE ANALISE - PLEITO DO CREDOR

interface CreditorClaim {
  classe: string[]
  coin: string[]
  creditorId: string[]
  value: number
}

const newCreditorClaim = async (claim: CreditorClaim) => {
  const { classe, coin, creditorId, value } = claim
  const results = []
  try {
    for (const id of creditorId) {
      const result = await api
        .post('/v1/creditors/claim/claim-creditor/',
          ({
            classes: {
              classe,
            },

            coins: {
              coin,
              value,
            },
            creditorId: id,
          }))
        .then((result: any) => result.claim)
      results.push(result)
    }
    return results
  }
  catch (error) {
    printError('ERROR ON NEW CREDITOR CLAIM', error)
  }
}

const updateCreditorClaim = async () => {
  api.put('/v1/creditors/notice/aj/')
    .then(({ analysis }: any) => analysis)
}

export default {
  getCreditors,
  newCreditor,
  updateCreditorClaim,
  getAnalysis,
  newAnalysis,
  newCreditorClaim,
}
