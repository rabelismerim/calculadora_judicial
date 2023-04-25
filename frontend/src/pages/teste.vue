<script setup lang="ts">
const newIncident = {
  creditorId: '33f72514-bd81-4f5c-9ec1-c787a7464b6e',
  description: ['Teste'],
}
let incident = $ref([''])

const newIncidente = async () => {
  try {
    const result = await calculationService.newIncident(newIncident)
    console.warn('print result', result)
  }
  catch (error) {
    printError('ERROR ON NEW CALCULATION:', error)
  }
}
const loadIncidente = async () => {
  try {
    const result = await calculationService.getIncident('33f72514-bd81-4f5c-9ec1-c787a7464b6e')
    incident = result
  }
  catch (error) {
    printError('ERROR ON LOAD CALCULATION:', error)
  }
}
</script>

<template>
  <div class="p-6 grid gap-4 justify-start">
    <h1>Teste</h1>
    <Btn
      label="Criar Calculo"
      @click="newIncidente"
    />
    <Btn
      label="Carregar Calculo"
      @click="loadIncidente"
    />
    <div>
      <pre>{{ incident }}</pre>
    </div>
  </div>
</template>
