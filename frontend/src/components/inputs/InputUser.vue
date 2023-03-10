<script setup lang="ts">
import type { ValidationRule } from 'quasar'
const props = withDefaults(defineProps<{
  modelValue: any
  label?: string
  rules?: ValidationRule<any>[]
  users?: any[]
}>(), {
  rules: () => ([]),
  users: () => ([]),
})
const emit = defineEmits(['update:modelValue'])
</script>

<template>
  <q-select
    :model-value="modelValue"
    :options="users"
    :label="label"
    outlined
    option-label="name"
    option-value="id"
    emit-value
    map-options
    @update:model-value="(value: number) => emit('update:modelValue', value)"
  >
    <template #option="scope">
      <q-item v-bind="scope.itemProps">
        <UserCell v-model="scope.opt" />
      </q-item>
    </template>
  </q-select>
</template>
