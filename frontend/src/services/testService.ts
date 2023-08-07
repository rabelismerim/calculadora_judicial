import axios from 'axios'

const BASE_URL = '/juca/api/v1/'
const TEST_TOKEN = 'c93d450fd6c88937f0a81c8d438579302cce2b01'

const getHeaders = () => {
  return {
    Authorization: TEST_TOKEN,
  }
}

export const testService = {
  async getData(id: string) {
    const url = `${BASE_URL}files/detail/${id}/`
    const headers = getHeaders()

    try {
      const response = await axios.get(url, { headers })
      return response.data
    }
    catch (error) {
      console.error('Erro ao obter os dados:', error)
      throw error
    }
  },
}
