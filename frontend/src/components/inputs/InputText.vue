<script setup lang="ts">
import type { ValidationRule } from 'quasar'
const props = withDefaults(defineProps<{
  modelValue: any
  label?: string
  rules?: ValidationRule<any>[]
}>(), {
  rules: () => ([]),
})
const emit = defineEmits(['update:modelValue'])
</script>

<template>
  <QInput
    :model-value="modelValue"
    :label="label"
    :rules="rules"
    outlined
    @update:model-value="value => emit('update:modelValue', value)"
  />
</template>
