<script setup lang="ts">
const newNotice = {
  classe: '1',
  coin: 'B',
  value: 50.0,
  creditorId: '92dd53a6-0db0-4e75-83a3-8f239e03af39',
}
let notice = $ref([''])

const setNotice = async () => {
  try {
    const result = await creditorsService.setNotice(newNotice)
    console.warn('print result', result)
  }
  catch (error) {
    printError('ERROR ON NEW NOTICE:', error)
  }
}
const loadNotice = async () => {
  try {
    const result = await creditorsService.getNotice()
    notice = result
  }
  catch (error) {
    printError('ERROR ON LOAD NOTICES:', error)
  }
}
</script>

<template>
  <div class="p-6 grid gap-4 justify-start">
    <h1>Teste</h1>
    <Btn
      label="Criar/Atualizar Notice"
      @click="setNotice"
    />
    <Btn
      label="Carregar Notice"
      @click="loadNotice"
    />
    <div>
      <pre>{{ notice }}</pre>
    </div>
  </div>
</template>
