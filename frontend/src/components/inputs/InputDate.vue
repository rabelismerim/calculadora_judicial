<script setup lang="ts">
import type { ValidationRule } from 'quasar'
const props = withDefaults(defineProps<{
  modelValue?: string | null
  label?: string
  rules?: ValidationRule<any>[]
  errorMessages?: any
  errorKey?: string
  disabled?: boolean
}>(), {
  rules: () => ([]),
  errorMessages: () => ({}),
  errorKey: '',
})
const emit = defineEmits(['update:modelValue', 'paste'])

const input = ref(null as any)
const hasError = computed(() => input.hasError)
const { clearError } = useBackendErrors(toRef(props, 'errorMessages'))
const dateData = computed({
  get: () => {
    if (!props.modelValue)
      return {}
    const [year, month, day] = props.modelValue
      ?.slice(0, 10)
      ?.split('-')
    return { day, month, year }
  },
  set: (value: any) => {
    const { day, month, year } = value
    const newDate = (day && month && year) ? [year, month, day].join('-') : ''
    if (props.errorKey)
      clearError(props.errorKey)
    emit('update:modelValue', newDate)
  },
})
const formatedDate = computed({
  get: () => {
    if (!dateData.value)
      return ''
    const { day, month, year } = dateData.value
    return [day, month, year]
      .filter(e => e)
      .join('/')
  },
  set: (value: string) => {
    if (value.match(/\d{4}-\d{2}-\d{2}.*/)) {
      const [year, month, day] = value?.slice(0, 10)?.split('-')
      dateData.value = { day, month, year }
      return
    }
    const [day, month, year] = value.split('/')
    dateData.value = { day, month, year }
  },
})
</script>

<template>
  <QInput
    ref="input"
    v-model="formatedDate"
    :label="label"
    :rules="rules"
    :error="!!errorMessages[errorKey]"
    :error-message="!!errorMessages[errorKey] ? errorMessages[errorKey] : ''"
    outlined
    mask="##/##/####"
    dense
    :disable="disabled"
    @paste="emit('paste', $event)"
  >
    <template #append>
      <div class="i-carbon-calendar cursor-pointer">
        <QPopupProxy
          cover
          transition-show="scale"
          transition-hide="scale"
        >
          <QDate
            v-model="formatedDate"
            mask="DD/MM/YYYY"
          >
            <div class="row items-center justify-end">
              <Btn
                v-close-popup
                label="Close"
                color="primary"
                flat
              />
            </div>
          </QDate>
        </QPopupProxy>
      </div>
    </template>
  </QInput>
</template>
