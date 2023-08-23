// UPLOAD
interface CreatePath {
  file: string
  path: string
  objectId: string
}

interface ErrorDetail {
  id: String
  createAtMin: Date
  createAtMax: Date
  updateAtMin: Date
  updateAtMax: Date
  status: String
}

const getFileDetail = (id: string) => api
  .get(`/v1/files/detail/${id}/`)
  .then((result: any) => result?.filedetail)

const getObjetcId = (path: string, objectId: string) => api
  .get(`/v1/files/detail/${path}/${objectId}/`)
  .then((result: any) => result?.objectId)

const getFilesExample = () => api
  .get('/v1/files/example/')
  .then((result: any) => result?.filesExample)

const getFilesExamplePath = (path: string) => api
  .get(`/v1/files/example/${path}/`)
  .then((result: any) => result?.excelNames)

const getFilesPathName = (path: string, name: string) => api
  .get(`/v1/files/example/${path}/${name}/`, { responseType: 'blob' })

const newCreatePath = async (createPath: CreatePath) => {
  const { file, path, objectId } = createPath
  const results = []
  try {
    const result = await api
      .post(`/v1/files/create/${path}/`,
        ({
          file,
          path,
          objectId,
        }))
      .then((result: any) => result.createPath)
    results.push(result)

    return results
  }
  catch (error) {
    printError('ERROR ON NEW CREATE PATH', error)
  }
}

const deleteErrorDetail = (errorId: string) => api

  .delete(`/v1/files/error/detail/${errorId}/`)

  .then(result => result?.data)

const putErrorDetail = async (updateErrorDetail: ErrorDetail) => {
  const { id, createAtMax, createAtMin, updateAtMax, updateAtMin, status } = updateErrorDetail
  const method = 'put'
  const results = []

  try {
    const result = await api[method](
      `/v1/files/error/detail/${id}/`,
      {
        id,
        createAtMax,
        createAtMin,
        updateAtMax,
        updateAtMin,
        status,
      },
    )
    results.push(result.data.updateErrorDetail)
    return results
  }
  catch (error) {
    printError('ERROR ON ERROR DETAIL', error)
  }
}

export default {
  getFileDetail,
  getObjetcId,
  getFilesExample,
  getFilesExamplePath,
  getFilesPathName,
  newCreatePath,
  deleteErrorDetail,
  putErrorDetail,
}
