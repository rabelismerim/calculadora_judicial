const getRates = () => api
  .get('/v1/rates/')
  .then((result: any) => result?.rates)

const getTemplates = () => api
  .get('/v1/rates/templates/')
  .then((result: any) => Object.values(result?.classeTemplates ?? {})
    .reduce((acc: any, { classe, templates }: any = {}) => {
      acc[classe?.classe] = templates
      return acc
    }, {}))

const getTemplate = (id: string) => api
  .get(`/v1/rates/templates/${id}/`)
  .then((result: any) => result?.template)

export default {
  getRates,
  getTemplates,
  getTemplate,
}
