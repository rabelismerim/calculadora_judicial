<script setup lang="ts">
const newAnalysis = {
  classe: '1',
  coin: 'B',
  recoveringsId: ['2b218f7d-f132-458a-8ab7-80a0c1c6c7a2'],
  value: 1000,
}
let analysis = $ref([''])

const createAnalysis = async () => {
  try {
    const result = await creditorsService.newAnalysis(newAnalysis)
    console.warn('print result', result)
  }
  catch (error) {
    printError('ERROR ON NEW CREDITOR:', error)
  }
}
const loadAnalysis = async () => {
  try {
    const result = await creditorsService.getAnalysis()
    analysis = result
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
      label="Criar Ficha de Analise"
      @click="createAnalysis"
    />
    <Btn
      label="Carregar Ficha de Analise"
      @click="loadAnalysis"
    />
    <div>
      <pre>{{ analysis }}</pre>
    </div>
  </div>
</template>
