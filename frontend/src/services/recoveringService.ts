const getRecoverings = () => api
  .get('/v1/recovering/')
  .then(({ data }) => data.recoverings.map(({
    id,
    project,
    process_number,
    entity,
  }: any) => ({
    id,
    projectId: project,
    processNumber: process_number,
    company: entity.name,
  })))

const getRecoveringArchive = () => api
  .get('/v1/recovering/archive_recovering/')
  .then(({ data }) => data)

export default {
  getRecoverings,
  getRecoveringArchive,
}
