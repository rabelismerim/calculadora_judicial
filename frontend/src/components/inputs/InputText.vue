<script setup lang="ts">
import type { ValidationRule } from 'quasar'
const props = withDefaults(defineProps<{
  modelValue: any
  label?: string
  rules?: ValidationRule<any>[]
  maxlength?: string | number
}>(), {
  rules: () => ([]),
})
const emit = defineEmits(['update:modelValue'])

const input = ref(null) as any
const hasError = computed(() => input.value.hasError)
</script>

<template>
  <QInput
    ref="input"
    :model-value="modelValue"
    :label="label"
    :rules="rules"
    :maxlength="maxlength"
    outlined
    dense
    @update:model-value="value => emit('update:modelValue', value)"
  />
</template>
