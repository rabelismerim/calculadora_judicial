<script setup lang="ts">
const newAnalysis = {
  classe: '1',
  coin: 'B',
  // recoveringsId: ['2b218f7d-f132-458a-8ab7-80a0c1c6c7a2'],
  value: 1000,
  creditorId: 'c7c5ab63-88e7-4129-b284-f7ba0297b16d',
}
let notice = $ref([''])

const createAnalysis = async () => {
  try {
    const result = await creditorsService.getCreditors('c7c5ab63-88e7-4129-b284-f7ba0297b16d')
    console.warn('print result', result)
  }
  catch (error) {
    printError('ERROR ON NEW CREDITOR:', error)
  }
}
const loadAnalysis = async () => {
  try {
    const result = await creditorsService.getNotice()
    notice = result
  }
  catch (error) {
    printError('ERROR ON LOAD CREDITORS:', error)
  }
}
</script>

<template>
  <div class="p-6 grid gap-4 justify-start">
    <h1>Teste</h1>
    <Btn
      label="Criar Credor"
      @click="createAnalysis"
    />
    <Btn
      label="Carregar Credor"
      @click="loadAnalysis"
    />
    <div>
      <pre>{{ notice }}</pre>
    </div>
  </div>
</template>
