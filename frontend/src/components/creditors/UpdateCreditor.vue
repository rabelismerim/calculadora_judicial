<script setup lang='ts'>
const props = withDefaults(defineProps<{
  modelValue: boolean
  creditor: any
  loading?: boolean
}>(), {
  modelValue: false,
  default: false,
})
const emit = defineEmits(['update:modelValue', 'update:creditor', 'update:loading', 'success', 'clear'])

let localLoading = $ref(false)
const form = ref(null as any)

const nullCreditor: any = {
  name: '',
  legalNumber: '',
  description: '',
  recovering: null,
}
let editingCreditor = $ref(clone(nullCreditor))

watchEffect(() => {
  editingCreditor = { ...props.creditor }
})
const clear = async () => {
  editingCreditor = clone(nullCreditor)
  emit('clear')
  await delay(0.1)
  form.value.reset()
}
const onSubmit = async () => {
  const isValid = await form.value.validate()
  if (!isValid)
    return
  localLoading = true
  emit('update:loading', true)
  try {
    const body = { ...editingCreditor }
    delete body.recovering
    const creditor = await creditorsService.updateCreditor(body)
    if (!creditor?.legalNumber)
      return
    notify({ message: 'O Credor foi atualizado com sucesso!' })
    emit('update:creditor', creditor)
    emit('update:modelValue', false)
  }
  catch (error) {
    printError('ERROR ON CREATE NEW CREDITOR:', error)
  }
  finally {
    localLoading = false
    emit('update:loading', false)
    emit('success')
    await delay(0.5)
    emit('clear')
  }
}
</script>

<template>
  <Modal
    :model-value="modelValue"
    :title="`Editar Credor: ${editingCreditor.name}`"
    hint="Vincular o Novo Credor às Recuperandas do Projeto."
    modal-class="max-w-200"
    @update:model-value="(value: boolean) => emit('update:modelValue', value)"
    @close="clear"
  >
    <QForm ref="form" @submit="onSubmit">
      <div class="grid sm:grid-cols-2 gap-x-6 gap-y-2 px-6 py-3">
        <InputText
          v-model="editingCreditor.name"
          label="Nome do Credor"
          :rules="[(value: any) => !!value || 'Este é um campo obrigatório!']"
          grow
        />
        <QInput
          v-model="editingCreditor.legalNumber"
          label="CPF/CNPJ"
          :rules="[(value: any) => !!value || 'Este é um campo obrigatório!']"
          disable
          grow
          outlined
        />
        <QInput
          v-model="editingCreditor.description"
          label="Descrição"
          outlined
          type="textarea"
          rows="3"
          class="mb-5 col-span-2"
        />
      </div>
      <div class="relative flex justify-end gap-2 p-3 border-t-1 ">
        <QLinearProgress
          v-if="localLoading"
          indeterminate
          color="secondary"
          class="absolute top-0 left-0"
          size="xs"
        />
        <Btn
          label="Atualizar Credor"
          type="button"
          :loading="localLoading"
          loading-label="Atualizando Credor..."
          :disabled="localLoading"
          @click="onSubmit"
        />
      </div>
    </QForm>
  </Modal>
</template>
