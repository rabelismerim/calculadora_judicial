<script setup lang="ts">
import type { ValidationRule } from 'quasar'

const props = withDefaults(defineProps<{
  modelValue: any
  label?: string
  rules?: ValidationRule<any>[]
  options?: any[]
  toAdd?: (evt: Event) => void
}>(), {
  rules: () => ([]),
  add: () => {},
  options: () => ([]),
})
const emit = defineEmits(['update:modelValue'])
</script>

<template>
  <QSelect
    :model-value="modelValue"
    :label="label"
    :rules="rules"
    outlined
    bottom-slots
    :options="options"
    counter
    maxlength="12"
    @update:model-value="value => emit('update:modelValue', value)"
  >
    <template #append>
      <QBtn
        round
        dense
        flat
        @click.stop.prevent="toAdd"
      >
        <div class="i-carbon-add" />
      </QBtn>
    </template>
  </QSelect>
</template>
