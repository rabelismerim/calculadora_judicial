<script setup lang='ts'>
const props = withDefaults(defineProps<{
  modelValue: boolean
  creditor: any
  options?: {
    recoverings: any[]
    ocurrences: any[]
    rates: any[]
  }
}>(), {
  modelValue: false,
  options: () => ({ recoverings: [], rates: [], ocurrences: [] }),
})
const emit = defineEmits(['update:modelValue', 'update:creditor', 'success', 'clear'])

let loading = $ref(false)
const form = ref(null as any)

const nullCreditor: any = {
  name: '',
  legalNumber: '',
  description: '',
  recoverings: [],
}
let editingCreditor = $ref(clone(nullCreditor))

watchEffect(() => {
  editingCreditor = clone(props.creditor)
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
  loading = true
  try {
    const { creditorsIds } = editingCreditor
    for (const _ of creditorsIds)
      await creditorsService.updateCreditor(editingCreditor)

    notify({ message: 'O Credor foi atualizado com sucesso!' })
    emit('update:modelValue', false)
    emit('success')
    emit('clear')
  }
  catch (error) {
    printError('ERROR ON CREATE NEW CREDITOR:', error)
  }
  finally {
    loading = false
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
        <InputLegal
          v-model="editingCreditor.legalNumber"
          :rules="[(value: any) => !!value || 'Este é um campo obrigatório!']"
          disable
          grow
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
          v-if="loading"
          indeterminate
          color="secondary"
          class="absolute top-0 left-0"
          size="xs"
        />
        <Btn
          label="Atualizar Credor"
          type="button"
          :loading="loading"
          loading-label="Atualizando Credor..."
          :disabled="loading"
          @click="onSubmit"
        />
      </div>
    </QForm>
  </Modal>
</template>
