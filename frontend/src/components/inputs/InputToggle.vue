<script setup lang="ts">
import type { ValidationRule } from 'quasar'
const props = withDefaults(defineProps<{
  modelValue?: boolean
  label?: string
  rules?: ValidationRule<any>[]
  errorMessages?: any
  errorKey?: string
  grow?: boolean
}>(), {
  rules: () => ([]),
  errorMessages: () => ({}),
  errorKey: '',
})
const emit = defineEmits(['update:modelValue'])

const input = ref(null as any)
const hasError = computed(() => input.value.hasError)
const { clearError } = useBackendErrors(toRef(props, 'errorMessages'))
const onInput = (value: boolean | null) => {
  if (props.errorKey)
    clearError(props.errorKey)
  emit('update:modelValue', !!value)
}
</script>

<template>
  <QToggle
    ref="input"
    :model-value="modelValue"
    :label="label"
    :rules="rules"
    :error="!!errorMessages[errorKey]"
    :error-message="!!errorMessages[errorKey] ? errorMessages[errorKey] : ''"
    outlined
    left-label
    :dense="!grow"
    class="justify-between"
    @update:model-value="onInput"
  />
</template>
