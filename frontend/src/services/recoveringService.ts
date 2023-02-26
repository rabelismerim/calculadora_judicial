const getRecovering = () => api
  .get('/v1/recovering/')
  .then(({ data }) => data.recoverings.map(({
    project,
    process_number,
    entity,
  }: any) => ({
    projectId: project,
    processNumber: process_number,
    company: entity.name,
  })))

const getRecoveringArchive = () => api
  .get('/v1/recovering/archive_recovering/')
  .then(({ data }) => data)

export default {
  getRecovering,
  getRecoveringArchive,
}
