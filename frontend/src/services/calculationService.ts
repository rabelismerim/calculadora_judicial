// CALCULO
interface Calculation {
  // classe: string[]
  // coin: string[]
  // value: number[]
  creditorId: string
  incidentId: string
  // description: string[]
  // calculationD: string[]
  appealCredit: boolean
  appealDeposit: boolean
  hasAdvocateHours: boolean
  creditAutorizationDate: string
  hasEdital: boolean
  recurralDeposit: number
}
const getCalculation = (id: string) => api
  .get(`/v1/calculation/${id}/`)
  .then(({ calculation }: any) => calculation)

const newCalculation = async (calculation: Calculation) => {
  const { creditorId, incidentId, appealCredit, appealDeposit, hasAdvocateHours, creditAutorizationDate, hasEdital, recurralDeposit } = calculation
  const results = []
  try {
    for (const id of creditorId) {
      const result = await api
        .post('/v1/calculation/',
          ({
          //   classes: {
          //     classe,
          //   },
          //   coins: {
          //     coin,
          //     value,
          //   },
            creditorId: id,
            incidentId,
            // verdict: {
            //   type_calculation: {
            //     description,
            //     calculationD,
            //   },
            //   description,
            //   value,
            // },
            appealCredit,
            appealDeposit,
            hasAdvocateHours,
            creditAutorizationDate,
            hasEdital,
            recurralDeposit,
          }))
        .then((result: any) => result.calculation)
      results.push(result)
    }
    return results
  }
  catch (error) {
    printError('ERROR ON NEW CREDITOR', error)
  }
}

interface Incident extends Calculation {
  number: string[]
}
const getIncident = (creditorId: string) => api
  .get(`/v1/calculation/creditor/${creditorId}/`)
  .then(({ incident }: any) => incident)

const newIncident = async (incident: Incident) => {
  const { number } = incident
  const results = []
  try {
    const result = await api
      .post('/v1/calculation/incident',
        ({
          number,
        }))
      // .then((result: any) => result.incident)
    results.push(result)
    return results
  }
  catch (error) {
    printError('ERROR ON NEW CREDITOR', error)
  }
}

// CALCULO - CRITERION

const getCriterion = (calculationId: string) => api

  .get(`/v1/calculation/criterion/${calculationId}/`)
  .then(({ criterion }: any) => criterion)

// CALCULO - VERDICT

interface Verdict {
  description: string
  calculation: string
  calculationId: string
  value: number
}

const getVerdict = (calculationId: string) => api

  .get(`/v1/calculation/verdict/${calculationId}`)
  .then(({ verdict }: any) => verdict)

const newVerdict = async (verdict: Verdict) => {
  const { description, calculation, calculationId, value } = verdict
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
          }))
        .then((result: any) => result.verdict)
      results.push(result)
    }
    return results
  }
  catch (error) {
    printError('ERROR ON NEW CREDITOR', error)
  }
}

// CALCULATION - FUNDS

interface Funds {
  calculationId: string
  name: string
}

const getFunds = (id: string) => api

  .get(`/v1/calculation/funds/${id}`)
  .then(({ funds }: any) => funds)

const newFunds = async (funds: Funds) => {
  const { calculationId, name } = funds
  const results = []
  try {
    for (const id of calculationId) {
      const result = await api
        .post('/v1/calculation/funds/',
          ({
            calculationId: id,
            name,
          }))
        .then((result: any) => result.funds)
      results.push(result)
    }
    return results
  }
  catch (error) {
    printError('ERROR ON NEW CREDITOR', error)
  }
}
interface FundsFunds {
  id?: string
  fundId: string
  dataBase: string
  historicalVue: number
  dsrReflexes: number
  summary: boolean
}

const getFundsFunds = (id: string) => api
  .get(`/v1/calculation/funds/funds/${id}/`)
  .then(({ fundsfunds }: any) => fundsfunds)

const setFundsFunds = async (fundsfunds: FundsFunds) => {
  const { id, fundId, dataBase, historicalVue, dsrReflexes, summary } = fundsfunds
  const method = id ? 'put' : 'post'
  const results = []
  try {
    for (const id of fundId) {
      const result = await api[method]('/v1/calculation/funds/funds/',
        ({
          ...fundsfunds,
          fundId: id,
          dataBase,
          historicalVue,
          dsrReflexes,
          summary,
        }))
        .then((result: any) => result.fundsfunds)
      results.push(result)
    }
    return results
  }
  catch (error) {
    printError('ERROR ON NEW CREDITOR', error)
  }
}

// CALCULATION - INTEGRATIONS

interface Integrations {
  id?: string
  fundId: string
  dataBase: Date
  historicalValue: number
  description: string
  summary: boolean
}

const getIntegrations = (id: string) => api

  .get(`/v1/calculation/funds/integrations/${id}/`)
  .then(({ integrations }: any) => integrations)

const setIntegrations = async (integrations: Integrations) => {
  const { id, fundId, dataBase, historicalValue, description, summary } = integrations
  const method = id ? 'put' : 'post'
  const results = []
  try {
    for (const id of fundId) {
      const result = await api[method]('/v1/calculation/funds/integrations/',
        ({
          ...integrations,
          fundId: id,
          dataBase,
          historicalValue,
          description,
          summary,
        }))
        .then((result: any) => result.statementsi)
      results.push(result)
    }
    return results
  }
  catch (error) {
    printError('ERROR ON NEW CREDITOR', error)
  }
}

// CALCULATION - DOCUMENT

interface Document {
  id?: string
  calculationId: string
  dataBase: Date
  historicalValue: number
  number: string
  name: string
}

const getDocument = (id: string) => api
  .get(`/v1/calculation/funds/documents/${id}`)
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
        .then((result: any) => result.document)
      results.push(result)
    }
    return results
  }
  catch (error) {
    printError('ERROR ON NEW CREDITOR', error)
  }
}

// CALCULATION - IRRF

interface IRRF {
  id?: string
  calculationId: string
  name: string
  monthsPeriod: number
}

const getIRRF = (id: string) => api
  .get(`/v1/calculation/funds/irrf/${id}/`)
  .then(({ irrf }: any) => irrf)

const newIRRF = async (irrf: IRRF) => {
  const { calculationId, name, monthsPeriod } = irrf
  const results = []
  try {
    for (const id of calculationId) {
      const result = await api
        .post('/v1/calculation/funds/irrf/',
          ({
            calculationId: id,
            name,
            monthsPeriod,
          }))
        .then((result: any) => result.fundIRRF)
      results.push(result)
    }
    return results
  }
  catch (error) {
    printError('ERROR ON NEW CREDITOR', error)
  }
}

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
      const result = await api[method]('/v1/calculation/funds/irrf/',
        ({
          ...fundsirrf,
          fundId: id,
          fundName,
          taxableAmounts,
        }))
        .then((result: any) => result.fundsirrf)
      results.push(result)
    }
    return results
  }
  catch (error) {
    printError('ERROR ON NEW CREDITOR', error)
  }
}

// CALCULATION - Comparative

interface Comparative {
  fundId: string
  fundName: string
  taxableAmounts: number
}

const getComparative = (calculationId: string) => api
  .get(`/v1/calculation/comparative/${calculationId}/`)
  .then(({ comparative }: any) => comparative)

const updateComparative = async (calculationId: string, body: any) => api
  .put(`/v1/calculation/comparative/${calculationId}`, body)
  .then(({ comparative }: any) => comparative)

// CALCULATION - Statement

const getStatement = (calculationId: string) => api

  .get(`/v1/calculation/statement/${calculationId}/`)
  .then(({ statement }: any) => statement)

// CALCULATION - Sheets Template

const getSheetsTemplate = (calculationId: string, exportType: string) => api

  .get(`/v1/calculation/export/${calculationId}/${exportType}`)
  .then(({ sheetstemplate }: any) => sheetstemplate)

export default {
  getCalculation,
  newCalculation,
  getIncident,
  newIncident,
  getCriterion,
  getVerdict,
  newVerdict,
  getFunds,
  newFunds,
  getFundsFunds,
  setFundsFunds,
  getIntegrations,
  setIntegrations,
  getDocument,
  setDocument,
  getIRRF,
  newIRRF,
  getFundsIRRF,
  setFundsIRRF,
  getComparative,
  updateComparative,
  getStatement,
  getSheetsTemplate,
}
