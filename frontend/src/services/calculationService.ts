const getCalculation = () => api
  .get('/v1/calculation/')
  .then(({ data }) => data)

const mapCalculation = (calculation: any) => {
  const {
    classe,
    coin,
    value,
    archive_json,
    creditor_id,
    incident_id,
    description,
    calculation_type,
    appeal_credit,
    appeal_deposit,
    has_advocative_hours,
    credit_authorization_date,
    has_edital,
  } = calculation

  return {
    calculation,
  }
}
const getUserCalculation = () => api
  .get('/v1/calculation/project_user/')
  .then(({ calculationtUser }: any) => [...new Set(calculationtUser)])
const getProjects = () => api
  .get('/v1/calculation/')
  .then((res: any) => res?.projects?.map(mapCalculation))
const getProject = (id: string) => api
  .get(`/v1/calculation/${id}/`)
  .then(({ calculation }: any) => calculation)
  .then(mapCalculation)
  .then((calculation: any) => {
    const { CalculationUsers = [] } = calculation

    calculation.participants = CalculationUsers.reduce((acc: any, current: any) => {
      const { firstName, lastName, username, userpicture, groups } = current
      const user = {
        picture: userpicture,
        fullName: `${firstName} ${lastName}`,
        email: `${username}@deloitte.com`,
      }
      groups.forEach(({ name }: any) => {
        if (!acc[name])
          acc[name] = []
        acc[name].push(user)
      })
      return acc
    }, {})

    return calculation
  })

export default {
  getCalculation,
  getUserCalculation,
}
