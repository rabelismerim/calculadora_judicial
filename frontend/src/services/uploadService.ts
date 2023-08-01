// UPLOAD
interface CreatePath {
  file: string
  path: string
  objectId: string
}

interface ErrorDetail {
  id: string
  createAtMin: Date
  createAtMax: Date
  updateAtMin: Date
  updateAtMax: Date
}

const getFileDetail = (id: string) => api
  .get(`/v1/files/detail/${id}/`)
  .then((result: any) => result?.filedetail)

const getObjetcId = (objectId: string) => api
  .get(`/v1/files/detail/{path}/${objectId}/`)
  .then((result: any) => result?.objectId)

const getFilesExample = () => api
  .get('/v1/files/example/')
  .then((result: any) => result?.filesExample)

const getFilesExamplePath = () => api
  .get('/v1/files/example/{path}/')
  .then((result: any) => result?.filesExamplePath)

const getFilesPathName = () => api
  .get('/v1/files/example/{path}/{name}/')
  .then((result: any) => result?.filesPathName)

const newCreatePath = async (createPath: CreatePath) => {
  const { file, path, objectId } = createPath
  const results = []
  try {
    const result = await api
      .post('/v1/files/create/{path}/',
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

const updateErrorDetail = async (updateerrordetail: ErrorDetail) => {
  const { id, createAtMax, createAtMin, updateAtMax, updateAtMin } = updateerrordetail
  const results = []
  try {
    const result = await api
      .post(`/v1/files/error/detail/${id}`,
        ({
          id,
          createAtMax,
          createAtMin,
          updateAtMax,
          updateAtMin,
        }))
      .then((result: any) => result.updateerrordetail)
    results.push(result)

    return results
  }
  catch (error) {
    printError('ERROR ON UPDATE ERROR DETAIL', error)
  }
}

export default {
  getFileDetail,
  getObjetcId,
  getFilesExample,
  getFilesExamplePath,
  getFilesPathName,
  newCreatePath,
  updateErrorDetail,
}
