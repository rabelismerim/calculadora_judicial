<script setup lang="ts">
const newIRRF = {
  fundId: 'c70162d2-c56e-49bd-9953-e3762f9091f3',
  fundName: 'Lisa Washington',
  taxableAmounts: 200,
}
let funds = $ref([''])

const newVerdicts = async () => {
  try {
    const result = await calculationService.setFundsIRRF(newIRRF)
    console.warn('print result', result)
  }
  catch (error) {
    printError('ERROR ON NEW INTEGRATION:', error)
  }
}
const loadFunds = async () => {
  try {
    const result = await calculationService.getFundsIRRF('c70162d2-c56e-49bd-9953-e3762f9091f3')
    funds = result
  }
  catch (error) {
    printError('ERROR ON LOAD INTEGRATION:', error)
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
