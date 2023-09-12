<script setup lang='ts'>
const props = withDefaults(defineProps<{
  modelValue: boolean
  creditor: any
  options?: {
    recoverings: any[]
  }
}>(), {
  modelValue: false,
  options: () => ({ recoverings: [] }),
})
const emit = defineEmits(['update:modelValue', 'update:creditor', 'success', 'clear'])

let loading = $ref(false)
const form = ref(null as any)

const creditorValidate: any = {
  name: '',
  legalNumber: '',
  description: '',
  recoverings: [],
}
let validateC = $ref(clone(creditorValidate))

watchEffect(() => {
  validateC = clone(props.creditor)
})
const clear = async () => {
  validateC = clone(creditorValidate)
  emit('clear')
  await delay(0.1)
  form.value.reset()
}
const onSubmit = async () => {
  const isValid = await form.value.validate()
  if (!isValid)
    return
  loading = true
  try {
    const { creditorsIds } = validateC
    for (const _ of creditorsIds)
      await creditorsService.updateCreditor(validateC, true)

    notify({ message: 'O Credor foi validado com sucesso!' })
    emit('update:modelValue', false)
    emit('success')
    emit('clear')
  }
  catch (error) {
    printError('ERROR ON VALIDATE NEW CREDITOR:', error)
  }
  finally {
    loading = false
  }
}
</script>

<template>
  <Modal
    :model-value="modelValue"
    :title="`Editar Credor: ${validateC.name}`"
    hint="Vincular o Novo Credor às Recuperandas do Projeto."
    modal-class="max-w-200"
    @update:model-value="(value: boolean) => emit('update:modelValue', value)"
    @close="clear"
  >
    <QForm ref="form" @submit="onSubmit">
      <div class="grid sm:grid-cols-2 gap-x-6 gap-y-2 px-6 py-3">
        <InputText
          v-model="validateC.name"
          label="Nome do Credor"
          :rules="[(value: any) => !!value || 'Este é um campo obrigatório!']"
          grow
        />
        <InputLegal
          v-model="validateC.legalNumber"
          :rules="[(value: any) => !!value || 'Este é um campo obrigatório!']"
          disable
          grow
        />
      </div>
      <div class="relative flex justify-end gap-2 p-3 border-t-1 ">
        <QLinearProgress
          v-if="loading"
          indeterminate
          color="secondary"
          class="absolute top-0 left-0"
          size="xs"
        />
        <Btn
          label="Validar Credor"
          type="button"
          :loading="loading"
          loading-label="Validando Credor..."
          :disabled="loading"
          @click="onSubmit"
        />
      </div>
    </QForm>
  </Modal>
</template>
