// VALIDAÇÃO UPLOAD

const getProjectId = (projectId: string) => api
  .get(`/v1/creditors/project/${projectId}/`)
  .then((result: any) => result?.file)

const getInactive = (projectId: string) => api
  .get(`/v1/creditors/project/inactive/${projectId}/`)
  .then((result: any) => result?.files)

const getDetailId = (id: string) => api
  .get(`/v1/creditors/detail/${id}/`)
  .then((result: any) => result?.files)

export default {
  getProjectId,
  getInactive,
  getDetailId,
}
