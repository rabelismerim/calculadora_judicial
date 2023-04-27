<script setup lang="ts">
const newFunds = {
  name: 'Teste Funds',
  calculationId: '761baf0d-940a-4233-8506-06fc540f3914',
}
let funds = $ref([''])

const newVerdicts = async () => {
  try {
    const result = await calculationService.newFunds(newFunds)
    console.warn('print result', result)
  }
  catch (error) {
    printError('ERROR ON NEW CALCULATION:', error)
  }
}
const loadFunds = async () => {
  try {
    const result = await calculationService.getFunds('')
    funds = result
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
      label="Criar Funds"
      @click="newVerdicts"
    />
    <Btn
      label="Carregar Funds"
      @click="loadFunds"
    />
    <div>
      <pre>{{ funds }}</pre>
    </div>
  </div>
</template>
