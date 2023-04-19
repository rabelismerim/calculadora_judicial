<script setup lang='ts'>
interface Creditor {
  name: string
  legalNumber: string
  recoveringsId: string[]
}
const props = withDefaults(defineProps<{
  modelValue: boolean
  creditor: Creditor
  options: any[]
}>(), {
  modelValue: false,
})
const emit = defineEmits(['update:modelValue', 'update:creditor'])

let loading = $ref(false)
const form = ref(null) as any

const mapOptions = computed(() => props?.options?.map(({ id: value, entity: { name: label } }) => ({ label, value })))

const nullCreditor: Creditor = {
  name: '',
  legalNumber: ' ',
  recoveringsId: [],
}
const newCreditor = computed({
  get() {
    return props.creditor
  },
  set(value: any) {
    emit('update:creditor', value)
  },
})
const clear = async () => {
  newCreditor.value = clone(nullCreditor)
  await delay(0.1)
  form.value.resetValidation ()
}
const onSubmit = async () => {
  if (newCreditor.value.id)
    return
  const isValid = await form.value.validate()
  if (!isValid)
    return
  loading = true
  try {
    const result: any = await creditorsService.createCreditor(newCreditor.value)
    if (result.filter((item: any) => !!item).length > 0) {
      notify({ message: `Credor ${newCreditor.value.name} foi criado com sucesso!` })
      clear()
      emit('update:modelValue', false)
    }
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
    :title="newCreditor?.id ? `Editar Credor: ${newCreditor.name}` : 'Cadastro de Credor'"
    hint="Vincular o Novo Credor às Recuperandas do Projeto."
    modal-class="max-w-200"
    @update:model-value="(value: boolean) => emit('update:modelValue', value)"
    @close="clear"
  >
    <QForm ref="form" @submit="onSubmit">
      <div class="grid sm:grid-cols-2 gap-x-6 gap-y-2 px-6 py-3">
        <InputText
          v-model="newCreditor.name"
          label="Nome do Credor"
          :rules="[(value: any) => !!value || 'Este é um campo obrigatório!']"
          grow
        />
        <InputLegal
          v-model="newCreditor.legalNumber"
          :rules="[(value: any) => !!value || 'Este é um campo obrigatório!']"
          grow
        />
        <QSelect
          v-model="newCreditor.recoveringsId"
          label="Recuperandas"
          outlined
          multiple
          emit-value
          map-options
          use-chips
          :options="mapOptions"
          :rules="[(value: any) => value.length > 0 || 'Este é um campo obrigatório!']"
          class="sm:col-span-2"
        >
          <template #no-option>
            <QItem>
              <QItemSection class="text-grey">
                Não existe Recuperanda Cadastrada
              </QItemSection>
            </QItem>
          </template>
        </QSelect>
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
          label="Cadastrar"
          tag="div"
          :loading="loading"
          loading-label="Criando Projeto..."
          :disabled="!!newCreditor.id"
          @click="onSubmit"
        />
      </div>
    </QForm>
  </Modal>
</template>
