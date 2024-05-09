// VALIDAÇÃO UPLOAD

const getProjectId = (projectId: string) => api
  .get(`/v1/creditors/project/${projectId}/`)
  .then((result: any) => result?.id)

const getDetailId = (id: string) => api
  .get(`/v1/creditors/detail/${id}/`)
  .then((result: any) => result?.detail)

export default {
  getProjectId,
  getDetailId,
}
