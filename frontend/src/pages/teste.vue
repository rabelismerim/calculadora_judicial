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

const newIncident = async () => {
  try {
    const result = await calculationService.newIncident({
      number: '10223230456',
    })
    console.warn(result)
  }
  catch (error) {
    printError('ERROR ON CREATE INCIDENT:', error)
  }
}
const newCalculation = async () => {
  try {
    const result = await calculationService.newCalculation({
      incidentId: '1bef8776-9055-4ce3-8111-5fac3c273cb2',
      creditorId: '5da447af-946b-47d9-8ee3-217fd751df6f',
    })
    console.warn(result)
  }
  catch (error) {
    printError('ERROR ON CREATE CALCULATION:', error)
  }
}
</script>

<template>
  <div class="p-6 grid gap-4 justify-start">
    <h1>Teste</h1>
    <div>
      <IconHint icon="i-carbon-enterprise" hint="this is a hint!" />
    </div>
    <Btn
      label="Criar Funds"
      @click="newVerdicts"
    />
    <Btn
      label="Carregar Funds"
      @click="loadFunds"
    />
    <Btn
      label="Criar Cálculo"
      @click="newCalculation"
    />
    <div>
      <pre>{{ funds }}</pre>
    </div>
  </div>
</template>
