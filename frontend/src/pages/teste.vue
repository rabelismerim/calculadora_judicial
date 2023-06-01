<script setup lang="ts">
const newCreditor = {
  name: 'Empresa Teste 4',
  legalNumber: '52.824.237/0001-90',
  recoveringsId: ['f84f063f-e944-4dfc-85e5-7ac04de04fdb', '2313d4a1-ee03-4e94-b86e-fd39b955c632', '2b218f7d-f132-458a-8ab7-80a0c1c6c7a2'],
}
let creditors = $ref([''])

const createCreditor = async () => {
  try {
    // const result = await creditorsService.createCreditor(newCreditor)
    // console.warn('print result', result)
  }
  catch (error) {
    printError('ERROR ON NEW CREDITOR:', error)
  }
}
const loadCreditors = async () => {
  try {
    const result = await creditorsService.getCreditors('227b3c32-7e7b-42f4-a10f-289c15aa1701')
    creditors = result
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
      label="Cadastrar Credor"
      @click="createCreditor"
    />
    <Btn
      label="Carregar Credores"
      @click="loadCreditors"
    />
    <div>
      <pre>{{ creditors }}</pre>
    </div>
  </div>
</template>
