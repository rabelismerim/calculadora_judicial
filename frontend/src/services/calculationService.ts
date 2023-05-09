// CALCULO
const getCalculation = (id: string) => api
  .get(`/v1/calculation/${id}/`)
  .then(({ calculation }: any) => calculation)
const getCalculations = (creditorId: string) => api
  .get(`/v1/calculation/creditor/${creditorId}/`)
  .then(({ calculations }: any) => calculations)

const newCalculation = async (calculation: any) => api
  .post('/v1/calculation/', calculation)
  .then((result: any) => result?.calculation)

const getIncidents = () => api
  .get('/v1/calculation/incident/')
  .then(({ incidents }: any) => incidents.map(({ id, number, historical }: any) =>
    ({ id, number, historical, description: number })))

const newIncident = async (number: string) => api
  .post('/v1/calculation/incident/', { number })
  .then(({ incident }: any) => incident)

// CALCULO - CRITERION

const getCriterion = (calculationId: string) => api
  .get(`/v1/calculation/criterion/${calculationId}/`)
  .then(({ criterion }: any) => criterion)

// CALCULO - VERDICT

interface Verdict {
  description: string
  descriptionC: string
  calculation: string
  calculationId: string
  value: number
}

const getVerdict = (calculationId: string) => api

  .get(`/v1/calculation/verdict/${calculationId}/`)
  .then(({ verdict }: any) => verdict)

const newVerdict = async (verdict: Verdict) => {
  const { description, descriptionC, calculation, calculationId, value } = verdict
  const results = []
  try {
    for (const id of calculationId) {
      const result = await api
        .post('/v1/calculation/verdict/',
          ({
            type_calculation: {
              description,
              calculation,
            },
            calculationId: id,
            value,
            descriptionC,
          }))
        .then((result: any) => result.verdict)
      results.push(result)
    }
    return results
  }
  catch (error) {
    printError('ERROR ON NEW VERDICT', error)
  }
}

// CALCULATION - FUNDS

interface Funds {
  id?: string
  fundId: string
  dataBase: string
  historicalVue: number
  dsrReflexes: number
  summary: boolean
}

const getFunds = (id: string) => api
  .get(`/v1/calculation/funds/labor/${id}/`)
  .then(({ fundsfunds }: any) => fundsfunds)

const setFunds = async (funds: Funds) => {
  const { id, fundId, dataBase, historicalVue, dsrReflexes, summary } = funds
  const method = id ? 'put' : 'post'
  const results = []
  try {
    for (const id of fundId) {
      const result = await api[method]('/v1/calculation/funds/labor/',
        ({
          ...funds,
          fundId: id,
          dataBase,
          historicalVue,
          dsrReflexes,
          summary,
        }))
        .then((result: any) => result.funds)
      results.push(result)
    }
    return results
  }
  catch (error) {
    printError('ERROR ON NEW FUNDS', error)
  }
}

// CALCULATION - INTEGRATIONS

interface Integrations {
  id?: string
  fundId: string
  dataBase: string
  historicalValue: number
  description: string
  summary: boolean
}

const getIntegrations = (id: string) => api

  .get(`/v1/calculation/funds/labor/integrations/${id}/`)
  .then(({ integrations }: any) => integrations)

const setIntegrations = async (integrations: Integrations) => {
  const { id, fundId, dataBase, historicalValue, description, summary } = integrations
  const method = id ? 'put' : 'post'
  const results = []
  try {
    for (const id of fundId) {
      const result = await api[method]('/v1/calculation/funds/labor/integrations/',
        ({
          ...integrations,
          fundId: id,
          dataBase,
          historicalValue,
          description,
          summary,
        }))
      results.push(result)
    }
    return results
  }
  catch (error) {
    printError('ERROR ON NEW INTEGRATIONS', error)
  }
}

// CALCULATION - DOCUMENT

interface Document {
  id?: string
  calculationId: string
  dataBase: string
  historicalValue: number
  number: string
  name: string
}

const getDocument = (id: string) => api
  .get(`/v1/calculation/funds/documents/${id}/`)
  .then(({ document }: any) => document)

const setDocument = async (document: Document) => {
  const { id, calculationId, dataBase, historicalValue, number, name } = document
  const method = id ? 'put' : 'post'
  const results = []
  try {
    for (const id of calculationId) {
      const result = await api[method]('/v1/calculation/funds/documents/',
        ({
          ...document,
          calculationId: id,
          statement: {
            dataBase,
            historicalValue,
            number,
          },
          name,
        }))
      results.push(result)
    }
    return results
  }
  catch (error) {
    printError('ERROR ON NEW DOCUMENTS', error)
  }
}

// CALCULATION - IRRF

interface FundsIRRF {
  id?: string
  fundId: string
  fundName: string
  taxableAmounts: number
}

const getFundsIRRF = (id: string) => api
  .get(`/v1/calculation/funds/irrf/funds/${id}/`)
  .then(({ fundsirrf }: any) => fundsirrf)

const setFundsIRRF = async (fundsirrf: FundsIRRF) => {
  const { id, fundId, fundName, taxableAmounts } = fundsirrf
  const method = id ? 'put' : 'post'
  const results = []
  try {
    for (const id of fundId) {
      const result = await api[method]('/v1/calculation/funds/irrf/funds/',
        ({
          ...fundsirrf,
          fundId: id,
          fundName,
          taxableAmounts,
        }))
      results.push(result)
    }
    return results
  }
  catch (error) {
    printError('ERROR ON NEW IRRF FUNDS', error)
  }
}

// CALCULATION - Comparative

interface Comparative {
  calculationId: string
  fundId: string
  fundName: string
  taxableAmounts: number
}

const getComparative = (calculationId: string) => api
  .get(`/v1/calculation/comparative/${calculationId}/`)
  .then(({ comparative }: any) => comparative)

const updateComparative = async (comparative: Comparative) => {
  const { calculationId, fundId, fundName, taxableAmounts } = comparative
  const results = []
  try {
    for (const id of fundId) {
      const result = await api
        .post(`/v1/calculation/comparative/${calculationId}/`,
          ({
            calculationId: id,
            fundId,
            fundName,
            taxableAmounts,
          }))
        .then((result: any) => result.comparative)
      results.push(result)
    }
    return results
  }
  catch (error) {
    printError('ERROR ON NEW CALCULATION', error)
  }
}

// CALCULATION - Statement

const getStatement = (calculationId: string) => api

  .get(`/v1/calculation/statement/${calculationId}/`)
  .then(({ statement }: any) => statement)

// CALCULATION - Sheets Template

const getSheetsTemplate = (calculationId: string, exportType: string) => api

  .get(`/v1/calculation/export/${calculationId}/${exportType}`)
  .then(({ sheetstemplate }: any) => sheetstemplate)

export default {
  newCalculation,
  getCalculation,
  getCalculations,
  newIncident,
  getIncidents,
  getCriterion,
  getVerdict,
  newVerdict,
  getFunds,
  setFunds,
  getIntegrations,
  setIntegrations,
  getDocument,
  setDocument,
  getFundsIRRF,
  setFundsIRRF,
  getComparative,
  updateComparative,
  getStatement,
  getSheetsTemplate,
}
