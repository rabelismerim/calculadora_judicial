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
  <q-input
    :model-value="modelValue"
    :label="label"
    :rules="rules"
    outlined
    mask="##/##/####"
    @update:model-value="value => emit('update:modelValue', value)"
  >
    <template #append>
      <div class="i-carbon-calendar cursor-pointer">
        <q-popup-proxy
          cover
          transition-show="scale"
          transition-hide="scale"
        >
          <q-date
            :model-value="modelValue"
            mask="DD/MM/YYYY"
            @update:model-value="value => emit('update:modelValue', value)"
          >
            <div class="row items-center justify-end">
              <q-btn
                v-close-popup
                label="Close"
                color="primary"
                flat
              />
            </div>
          </q-date>
        </q-popup-proxy>
      </div>
    </template>
  </q-input>
</template>
