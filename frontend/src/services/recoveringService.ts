const getRecoverings = () => api
  .get('/v1/recovering/')
  .then((result: any) => result?.recoverings?.map((recovering: any) => {
    const { entity } = recovering
    return {
      ...recovering,
      company: entity.name,
    }
  }))

const getRecoveringArchive = () => api
  .get('/v1/recovering/archive_recovering/')

export default {
  getRecoverings,
  getRecoveringArchive,
}
