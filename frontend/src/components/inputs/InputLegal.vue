<script setup lang="ts">
import type { ValidationRule } from 'quasar'
const props = withDefaults(defineProps<{
  modelValue: any
  label?: string
  rules?: ValidationRule<any>[]
  errorMessages?: any
  errorKey?: string
  grow?: boolean
}>(), {
  label: 'CPF / CNPJ',
  rules: () => ([]),
  errorMessages: () => ({}),
  errorKey: '',
})
const emit = defineEmits(['update:modelValue'])
let isCPF = $ref(true)
watchEffect(() => {
  isCPF = (props.modelValue || '').toString().replace(/[^0-9]/g, '').length <= 11
})

const input = ref(null as any)
const hasError = computed(() => input.value.hasError)
const { clearError } = useBackendErrors(toRef(props, 'errorMessages'))
const onInput = (value: string | number | null) => {
  if (props.errorKey)
    clearError(props.errorKey)
  emit('update:modelValue', value)
}
const onPaste = (evt: ClipboardEvent) => {
  const clipBoardData = evt?.clipboardData?.getData('text') || ''
  const value = clipBoardData.replace(/[^0-9]/g, '')
  isCPF = value.length <= 11
  emit('update:modelValue', value)
}
</script>

<template>
  <QInput
    ref="input"
    :model-value="modelValue"
    :label="label"
    :maxlength="18"
    :mask="modelValue.length <= 14 && isCPF ? '###.###.###-###' : '##.###.###/####-##'"
    :rules="[
      ...rules,
      value => !value || value.length === 14 || value.length === 18 || 'Precisa ser um CPF ou um CNPJ',
      value => !value || value.length === 18 || value.length === 14 && isValidCPF(value) || 'CPF não é válido',
      value => !value || value.length === 14 || value.length === 18 && isValidCNPJ(value) || 'CNPJ não é válido',
    ]"
    :error="!!errorMessages[errorKey]"
    :error-message="!!errorMessages[errorKey] ? errorMessages[errorKey] : ''"
    outlined
    :dense="!grow"
    @update:model-value="onInput"
    @paste.prevent="onPaste"
  />
</template>
