<script setup lang='ts'>
const props = withDefaults(defineProps<{
  modelValue: boolean
  options: any
  rates: any[]
  calculationId: string
}>(), {

})
const emit = defineEmits(['update:modelValue', 'success'])

let loading = $ref(false)
let newCredit = $ref({} as any)
const newCreditForm = ref(null as any)

let templates = $ref({} as any)
const loadTemplates = async () => {
  templates = await ratesService.getTemplates()
}
const loadTemplate = async (id: string) => {
  if (!id)
    return
  const result = await ratesService.getTemplate(id)
  newCredit.endPoint = result?.endPoint
  const fields = result?.fields?.map(({ id, key, label, default: fallback, order, required, typeDisplay, choices }: any) => ({
    id,
    key,
    label,
    order,
    type: typeDisplay,
    choices,
    required,
    fallback,
  }))
  const defaultValues = fields
    ?.filter(({ fallback }: any) => fallback !== null)
    ?.map(({ fallback, key }: any) => [key, fallback])
  if (defaultValues?.length > 0)
    defaultValues.forEach(([key, value]: [string, any]) => newCredit[key] = value)
  newCredit.fields = fields
    .sort(({ order: a }: any, { order: b }: any) => a - b)
}

const clearNewCredit = () => {
  newCredit = {}
  newCreditForm.value.reset()
  emit('update:modelValue', false)
}

const host = import.meta.env.VITE_API_HOST
const createCredit = async () => {
  const { classId, coinId, rateId, templateId, endPoint } = newCredit
  if (!endPoint)
    return

  try {
    loading = true
    const endPointNewCredit = endPoint.replace('/juca/api/', '')
    const result: any = await api.post(endPointNewCredit, {
      ...newCredit,
      classes: {
        classe: classId,
      },
      coins: {
        coin: coinId,
      },
      rateId,
      templateId,
      calculationId: props.calculationId,
    })
    if (result) {
      notify({ message: 'Crédito Criado com Sucesso!' })
      clearNewCredit()
      emit('success')
    }
  }
  catch (error) {
    printError('ERROR ON CREATING CREDIT:', error)
  }
  finally {
    loading = false
  }
}

const isRequired = ({ required }: any) => required && [(value: any) => !!value || 'Campo obrigatório!']

const filterInput = $ref('')
const filteredTemplates = computed(() => (templates[newCredit.classId] ?? [])
  ?.filter(({ name }: any) => name.toLowerCase().includes(filterInput.toLowerCase())))

onMounted(async () => {
  await loadTemplates()
})
</script>

<template>
  <Modal
    :model-value="modelValue"
    title="Criar Novo Credito"
    hint="Vincular um Novo Crédito à este Cálculo."
    modal-class="max-w-200"
    @close="clearNewCredit"
  >
    <QForm ref="newCreditForm" @submit.prevent="createCredit">
      <div class="p-4 grid grid-cols-2 gap-x-4">
        <QSelect
          v-model="newCredit.classId"
          :options="options?.classesOptions"
          label="Classe"
          outlined
          emit-value
          map-options
          option-value="id"
          option-label="legend"
          :rules="[(value: string) => !!value || 'Este Campo é obrigatório!']"
          :disable="loading"
          dense
          @update:model-value="newCredit.templateId = null"
        />
        <QSelect
          v-model="newCredit.templateId"
          :options="filteredTemplates"
          label="Tipo"
          outlined
          use-input
          emit-value
          map-options
          option-value="id"
          option-label="name"
          :disable="loading"
          :rules="[(value: string) => !!value || 'Este Campo é obrigatório!']"
          dense
          @input-value="(value: string) => filterInput = value"
          @update:model-value="(value: string) => loadTemplate(value)"
        />
        <QSelect
          v-model="newCredit.coinId"
          :options="options?.coinOptions"
          label="Moeda"
          outlined
          emit-value
          map-options
          option-value="id"
          option-label="legend"
          :rules="[(value: string) => !!value || 'Este Campo é obrigatório!']"
          :disable="loading"
          dense
        />
        <div v-for="field in newCredit?.fields as any[]" :key="field.id">
          <QInput
            v-if="field.type === 'text'"
            v-model="newCredit[field.key]"
            :label="field.label"
            :rules="isRequired(field)"
            outlined
            dense
          />
          <QInput
            v-else-if="field.type === 'float' || field.type === 'integer'"
            v-model="newCredit[field.key]"
            :label="field.label"
            :rules="isRequired(field)"
            type="number"
            :step="field.type === 'float' ? 'any' : 1"
            outlined
            dense
            @update:model-value="(value: number | string | null) => (field.type === 'integer') && (newCredit[field.key] = Math.round(value as number))"
          />
          <QSelect
            v-else-if="field.type === 'choice'"
            v-model="newCredit[field.key]"
            :label="field.label"
            :rules="isRequired(field)"
            :options="field.choices"
            option-label="legend"
            option-value="id"
            emit-value
            map-options
            outlined
            dense
          />
          <QToggle
            v-else-if="field.type === 'boolean'"
            v-model="newCredit[field.key]"
            :label="field.label"
            left-label
          />
          <InputDate
            v-else-if="field.type === 'date'"
            v-model="newCredit[field.key]"
            :rules="isRequired(field)"
            :label="field.label"
            dense
          />
          <div v-else>
            {{ field.label }} - {{ field.key }} - {{ field.type }}
          </div>
        </div>
      </div>
      <div class="border-1 border-t-black/12 p-4 flex justify-end relative">
        <QLinearProgress
          v-if="loading"
          indeterminate
          color="secondary"
          class="absolute top-0 left-0"
          size="xs"
        />
        <Btn
          type="submit"
          label="Criar Crédito"
          :loading="loading"
          loading-label="Criando Crédito..."
        />
      </div>
    </QForm>
  </Modal>
</template>
