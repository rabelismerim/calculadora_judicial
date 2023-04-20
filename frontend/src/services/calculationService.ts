// CALCULO
interface Calculation {
  classe: string
  coin: string
  value: number

}
const getCalculation = (creditorId: string) => api
  .get(`/v1/calculation/creditor/${creditorId}/`)
  .then(({ calculation }: any) => calculation)

const newCalculation = async (calculation: Calculation) => {
  const { description, calculation, calculationId, value } = calculation
  const results = []
  try {
    for (const id of calculationId) {
      const result = await api
        .post('/v1/calculation/',
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

const getVerdict = () => api

  .get('/v1/calculation/verdict/')
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

// CALCULATION - FUNDS - VERBAS

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

const updateFunds = async (id: string) => {
  api.put(`/v1/calculation/funds/funds/${id}`)
    .then(({ funds }: any) => funds)
}

// CALCULATION - STATEMENST FUNDS - EXTRAT. VERBAS

interface StatementsF {
  fundId: string
  dataBase: Date
  historicalValue: number
  dsrReflexes: number
  summary: boolean
}

const getStatementsF = () => api

  .get('/v1/calculation/funds/funds/')
  .then(({ statementsf }: any) => statementsf)

const newStatementsF = async (statementsf: StatementsF) => {
  const { fundId, dataBase, historicalValue, dsrReflexes, summary } = statementsf
  const results = []
  try {
    for (const id of fundId) {
      const result = await api
        .post('/v1/calculation/funds/funds/',
          ({
            fundId: id,
            dataBase,
            historicalValue,
            dsrReflexes,
            summary,
          }))
        .then((result: any) => result.statementsf)
      results.push(result)
    }
    return results
  }
  catch (error) {
    printError('ERROR ON NEW CREDITOR', error)
  }
}

const updateStatementsF = async () => {
  api.put('/v1/calculation/funds/funds/')
    .then(({ statementsf }: any) => statementsf)
}

// CALCULATION - STATEMENST INTEGRATIONS - EXTRAT. VERBAS

interface StatementsI {
  fundId: string
  dataBase: Date
  historicalValue: number
  description: string
  summary: boolean
}

const getStatementsI = (id: string) => api

  .get(`/v1/calculation/funds/integrations/${id}/`)
  .then(({ statementsi }: any) => statementsi)

const newStatementsI = async (statementsi: StatementsI) => {
  const { fundId, dataBase, historicalValue, description, summary } = statementsi
  const results = []
  try {
    for (const id of fundId) {
      const result = await api
        .post('/v1/calculation/funds/integrations/',
          ({
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

const updateStatementsI = async (id: string) => {
  api.put(`/v1/calculation/funds/integrations/${id}/`)
    .then(({ statementsi }: any) => statementsi)
}

// CALCULATION - FUND DOCUMENT - VERBAS DOCS

interface FundDoc {
  calculationId: string
  dataBase: Date
  historicalValue: number
  number: string
  name: string
}

const getFundDoc = () => api

  .get('/v1/calculation/funds/documents/')
  .then(({ funddoc }: any) => funddoc)

const newFundDoc = async (funddoc: FundDoc) => {
  const { calculationId, dataBase, historicalValue, number, name } = funddoc
  const results = []
  try {
    for (const id of calculationId) {
      const result = await api
        .post('/v1/calculation/funds/documents/',
          ({
            calculationId: id,
            statement: {
              dataBase,
              historicalValue,
              number,
            },
            name,
          }))
        .then((result: any) => result.funddoc)
      results.push(result)
    }
    return results
  }
  catch (error) {
    printError('ERROR ON NEW CREDITOR', error)
  }
}

// CALCULATION - STATEMENT FUND DOCUMENTS - EXTRAT. VERBAS DOC

interface StatementFDocs {
  dataBase: Date
  historicalValue: number
  number: string
}

const getStatementFDocs = (id: string) => api

  .get(`/v1/calculation/funds/documents/funds/${id}`)
  .then(({ statementdoc }: any) => statementdoc)

const updateStatementFDocs = async (id: string) => {
  api.put(`/v1/calculation/funds/documents/funds/${id}`)
    .then(({ statementdoc }: any) => statementdoc)
}

// CALCULATION - Fund IRRF - VERBAS IRRF

interface FundIRRF {
  calculationId: string
  name: string
  monthsPeriod: number
}

const getFundIRRF = () => api

  .get('/v1/calculation/funds/irrf/')
  .then(({ fundIRRF }: any) => fundIRRF)

const newFundIRRF = async (fundIRRF: FundIRRF) => {
  const { calculationId, name, monthsPeriod } = fundIRRF
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

// CALCULATION - Comparative

interface Comparative {
  fundId: string
  fundName: string
  taxableAmounts: number
}
interface NewComparative extends Comparative {

}
const getComparative = () => api
  .get('/v1/calculation/comparative')
  .then(({ comparative }: any) => comparative)

const updateComparative = async (calculationId: string, body: any) => api
  .put(`/v1/calculation/comparative/${calculationId}`, body)
  .then(({ comparative }: any) => comparative)

// CALCULATION - Statement IRRF - Extrato de verbas IRRF

interface StatementsIRRF {
  fundId: string
  fundName: string
  taxableAmounts: number
}

const getStatementsIRRF = (id: string) => api

  .get(`/v1/calculation/funds/irrf/funds/${id}`)
  .then(({ statementsirrf }: any) => statementsirrf)

const newStatementsIRRF = async (statementsirrf: StatementsIRRF) => {
  const { fundId, fundName, taxableAmounts } = statementsirrf
  const results = []
  try {
    for (const id of fundId) {
      const result = await api
        .post('/v1/calculation/funds/irrf/funds/',
          ({
            fundId: id,
            fundName,
            taxableAmounts,
          }))
        .then((result: any) => result.statementsirrf)
      results.push(result)
    }
    return results
  }
  catch (error) {
    printError('ERROR ON NEW CREDITOR', error)
  }
}

const updateStatementsIRRF = async (id: string) => {
  api.put(`/v1/calculation/funds/irrf/funds/${id}`)
    .then(({ statementsirrf }: any) => statementsirrf)
}

// CALCULATION - Statement - Extrato contábil

const getStatementEXT = () => api

  .get('/v1/calculation/statement')
  .then(({ statementext }: any) => statementext)

export default {
  getCalculation,
  getCriterion,
  getVerdict,
  newVerdict,
  getFunds,
  newFunds,
  updateFunds,
  getStatementsF,
  newStatementsF,
  updateStatementsF,
  getStatementsI,
  newStatementsI,
  updateStatementsI,
  getFundDoc,
  newFundDoc,
  getStatementFDocs,
  updateStatementFDocs,
  getFundIRRF,
  newFundIRRF,
  getStatementsIRRF,
  newStatementsIRRF,
  updateStatementsIRRF,
  getComparative,
  updateComparative,
  getStatementEXT,
}
