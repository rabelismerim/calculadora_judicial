const mapCalculation = (calculation: any) => {

}

// CALCULO - CRITERION

const getCriterion = () => api

  .get(`/v1/calculation/criterion/${calculation_id}/`)
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

export default {
  getCriterion,
  getVerdict,
  newVerdict,
}
