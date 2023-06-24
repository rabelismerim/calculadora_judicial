const getRates = () => api
  .get('/v1/rates/')
  .then((result: any) => result?.rates)

const getTemplates = () => api
  .get('/v1/rates/templates/')
  .then((result: any) => result?.templates)

const getTemplate = (id: string) => api
  .get(`/v1/rates/templates/${id}/`)
  .then((result: any) => result?.template)

export default {
  getRates,
  getTemplates,
  getTemplate,
}
