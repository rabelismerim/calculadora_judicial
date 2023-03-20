<script setup lang="ts">
import type { ValidationRule } from 'quasar'
const props = withDefaults(defineProps<{
  modelValue: any
  label?: string
  rules?: ValidationRule<any>[]
  errorMessages?: any
  errorKey?: string
}>(), {
  rules: () => ([]),
  errorMessages: () => ({}),
  errorKey: '',
})
const emit = defineEmits(['update:modelValue'])

const input = ref(null) as any
const hasError = computed(() => input.hasError)
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
    :error="!!errorMessages[errorKey]"
    :error-message="!!errorMessages[errorKey] ? errorMessages[errorKey] : ''"
    outlined
    mask="##/##/####"
    dense
    @update:model-value="onInput"
  >
    <template #append>
      <div class="i-carbon-calendar cursor-pointer">
        <QPopupProxy
          cover
          transition-show="scale"
          transition-hide="scale"
        >
          <QDate
            :model-value="modelValue"
            mask="DD/MM/YYYY"
            @update:model-value="onInput"
          >
            <div class="row items-center justify-end">
              <Btn
                v-close-popup
                label="Close"
                color="primary"
                flat
              />
            </div>
          </QDate>
        </QPopupProxy>
      </div>
    </template>
  </QInput>
</template>
