<script setup lang="ts">
import type { ValidationRule } from 'quasar'
const props = withDefaults(defineProps<{
  modelValue: any
  label?: string
  rules?: ValidationRule<any>[]
  maxlength?: string | number
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

const input = ref(null) as any
const hasError = computed(() => input.value.hasError)
const { clearError } = useBackendErrors(toRef(props, 'errorMessages'))
const onInput = (value: string | number | null) => {
  if (props.errorKey)
    clearError(props.errorKey)
  emit('update:modelValue', value)
}
</script>

<template>
  <QInput
    ref="input"
    :model-value="modelValue"
    :label="label"
    :maxlength="maxlength"
    :mask="modelValue.length <= 14 ? '###.###.###-###' : '##.###.###/####-##'"
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
  />
</template>
