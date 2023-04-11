const mapCreditor = (creditor: any) => {

}

const mapAnalysi = (creditor: any) => {
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
  .then(({ creditors }: any) => creditors)
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
    printError('ERROR ON NEW CREDITOR', error)
  }
}

// FICHA DE ANALISE - EDITAL DA AJ
const getAnalysis = () => api
  .get('/v1/creditors/notice/aj/')
  .then(({ analysis }: any) => analysis)
const newAnalysi = (name: string) => api
  .post('/v1/creditors/', { name })
  .then(({ analysis }: any) => analysis)
  .then(({ name, id }) => ({ name, id }))

export default {
  getCreditors,
  newCreditor,
  getAnalysis,
}
