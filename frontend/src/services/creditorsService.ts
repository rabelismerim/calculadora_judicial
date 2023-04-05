const mapCreditor = (creditor: any) => {
  const {
    name,
    legal_number,
    recovering_id,
    rate_id,
    classe,
    coin,
    value,
    archive_json,
    notice_recovering,
    admission,
    dismissal,
    default_interest,
    fine,
    advocative_hours,
    description,
  } = creditor
}
// CREDITOR
const getCreditor = () => api
  .get('/v1/creditors/')
  .then(({ creditor }: any) => creditor)
  .then(data => data.map(({ name, id }: any) => ({ name, id })))
const newCreditor = (name: string) => api
  .post('/v1/creditors/', { name })
  .then(({ creditor }: any) => creditor)
  .then(({ description, id }) => ({ description, id }))


export default {
  getCreditor,
}
