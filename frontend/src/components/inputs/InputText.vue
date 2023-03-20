<script setup lang="ts">
import type { ValidationRule } from 'quasar'
const props = withDefaults(defineProps<{
  modelValue: any
  label?: string
  rules?: ValidationRule<any>[]
  maxlength?: string | number
  errorMessages?: any
  errorKey?: string
}>(), {
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
    :rules="rules"
    :maxlength="maxlength"
    :error="!!errorMessages[errorKey]"
    :error-message="!!errorMessages[errorKey] ? errorMessages[errorKey] : ''"
    outlined
    dense
    @update:model-value="onInput"
  />
</template>
