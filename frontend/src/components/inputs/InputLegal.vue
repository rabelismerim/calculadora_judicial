<script setup lang="ts">
import type { ValidationRule } from 'quasar'
const props = withDefaults(defineProps<{
  modelValue: any
  label?: string
  rules?: ValidationRule<any>[]
  maxlength?: string | number
}>(), {
  label: 'CPF / CNPJ',
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
    :maxlength="maxlength"
    :mask="modelValue.length <= 14 ? '###.###.###-###' : '##.###.###/####-##'"
    :rules="[
      ...rules,
      value => value.length === 14 || value.length === 18 || 'Precisa ser um CPF ou um CNPJ',
    ]"
    outlined
    dense
    @update:model-value="value => emit('update:modelValue', value)"
  />
</template>
