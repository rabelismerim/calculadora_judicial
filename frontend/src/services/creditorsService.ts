// CREDORES
interface Creditor {
  name: string
  legalNumber: string
  recoveringsId: string[]
}
interface Detail extends Creditor {
  description: string
}
interface Options extends Creditor {
  legend: string
}
const getCreditors = (id: string) => api
  .get(`/v1/creditors/project/${id}/`)
  .then(({ creditors }: any) => creditors)

const getDetail = (id: string) => api
  .get(`/v1/creditors/detail/${id}/`)
  .then(({ detail }: any) => detail)

const getOptions = () => api
  .get('/v1/creditors/options/')
  .then(({ options }: any) => options)

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

const updateCreditors = async (id: string, body: any) => api
  .put(`/v1/creditors/${id}`, body)
  .then(({ creditors }: any) => creditors)

// // FICHA DE ANALISE - EDITAL DA AJ

// interface Notice {
//   classe: string[]
//   coin: string[]
//   recoveringsId: string[]
//   value: number
// }
// interface Recovering extends Notice {
//   creditorId: string[]
// }

// const getNotice = () => api
//   .get('/v1/creditors/notice/aj/')
//   .then(({ analysis }: any) => analysis)
// const newNotice = async (notice: Notice) => {
//   const { classe, coin, recoveringsId, value } = notice
//   const results = []
//   try {
//     for (const id of recoveringsId) {
//       const result = await api
//         .post('/v1/creditors/notice/aj/',
//           ({
//             classes: {
//               classe,
//             },

//             coins: {
//               coin,
//               value,
//             },
//             recoveringsId: id,
//           }))
//         .then((result: any) => result.notice)
//       results.push(result)
//     }
//     return results
//   }
//   catch (error) {
//     printError('ERROR ON NEW ANALYSIS', error)
//   }
// }

// FICHA DE ANALISE - EDITAL DA AJ

interface Notice {
  classe: string[]
  coin: string[]
  value: number
  creditorId: string[]
  // recoveringsId: string[]
}
interface Recovering extends Notice {}

const getNotice = () => api
  .get('/v1/creditors/notice/aj/')
  .then(({ notice }: any) => notice)
const newNotice = async (notice: Notice) => {
  const { classe, coin, creditorId, value } = notice
  const results = []
  try {
    for (const id of creditorId) {
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
            creditorId: id,
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
const updateNotice = async (id: string, body: any) => api
  .put(`/v1/creditors/notice/aj/${id}/`, body)
  .then(({ notice }: any) => notice)

const getRecoverings = () => api
  .get('/v1/creditors/notice/recovering/')
  .then(({ recoverings }: any) => recoverings)

const newRecovering = async (recovering: Recovering) => {
  const { classe, coin, creditorId, value } = recovering
  const results = []
  try {
    for (const id of creditorId) {
      const result = await api
        .post('/v1/creditors/notice/recovering/',
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
        .then((result: any) => result.recovering)
      results.push(result)
    }
    return results
  }
  catch (error) {
    printError('ERROR ON NEW ANALYSIS', error)
  }
}

const updateRecovering = async (id: string, body: any) => api
  .put(`/v1/creditors/notice/recovering/${id}`, body)
  .then(({ recovering }: any) => recovering)

// // FICHA DE ANALISE - PLEITO DO CREDOR

// interface CreditorClaim {
//   classe: string[]
//   coin: string[]
//   creditorId: string[]
//   value: number
// }

// const newCreditorClaim = async (claim: CreditorClaim) => {
//   const { classe, coin, creditorId, value } = claim
//   const results = []
//   try {
//     for (const id of creditorId) {
//       const result = await api
//         .post('/v1/creditors/claim/claim-creditor/',
//           ({
//             classes: {
//               classe,
//             },

//             coins: {
//               coin,
//               value,
//             },
//             creditorId: id,
//           }))
//         .then((result: any) => result.claim)
//       results.push(result)
//     }
//     return results
//   }
//   catch (error) {
//     printError('ERROR ON NEW CREDITOR CLAIM', error)
//   }
// }

// const updateCreditorClaim = async () => {
//   api.put('/v1/creditors/notice/aj/')
//     .then(({ analysis }: any) => analysis)
// }

export default {
  getCreditors,
  getDetail,
  getOptions,
  newCreditor,
  updateCreditors,
  getNotice,
  newNotice,
  updateNotice,
  // newCreditorClaim,
  // updateCreditorClaim,
  getRecoverings,
  newRecovering,
  updateRecovering,
}
