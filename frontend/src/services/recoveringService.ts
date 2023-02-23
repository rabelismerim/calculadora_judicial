const getRecovering = () => api
  .get('/v1/recovering/')
  .then(({ data }) => data)

const getRecoveringArchive = () => api
  .get('/v1/recovering/archive_recovering/')
  .then(({ data }) => data)

export default {
  getRecovering,
  getRecoveringArchive,
}
