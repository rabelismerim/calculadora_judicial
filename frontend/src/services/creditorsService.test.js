import { describe, expect, it } from 'vitest'
import creditorsService from '@/services/creditorsService'

describe('Get Creditors', async () => {
  it('should return an Array', async () => {
    let data
    try {
      data = await creditorsService.getCreditors('227b3c32-7e7b-42f4-a10f-289c15aa1701')
      console.warn('CREDITORS:', data)
    }
    catch (error) {
      console.warn('ERROR ON LOADING CREDITORS:', error)
    }
    expect(data).toBeInstanceOf(Array)
  })
})
