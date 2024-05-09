const getRates = () => api
  .get('/v1/rates/')

const getTemplates = () => api
  .get('/v1/rates/templates/')
  .then((result: any) => result
    ?.reduce((acc: any, { classe, templates }: any = {}) => {
      acc[classe?.classe] = templates
      return acc
    }, {}))

const getTemplate = (id: string) => api
  .get(`/v1/rates/templates/${id}/`)

export default {
  getRates,
  getTemplates,
  getTemplate,
}
