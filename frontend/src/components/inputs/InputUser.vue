<script setup lang="ts">
import type { ValidationRule } from 'quasar'
const props = withDefaults(defineProps<{
  modelValue: any
  label?: string
  rules?: ValidationRule<any>[]
  users?: any[]
  errorMessages?: any
  errorKey?: string
}>(), {
  rules: () => ([]),
  users: () => ([]),
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

let options = $ref(props.users)
const onFilter = (val: string, update: any) => {
  update(() => {
    const needle = val.toLowerCase()
    options = props.users.filter(({ fullName }) => fullName?.toLowerCase()?.includes(needle))
  })
}
</script>

<template>
  <QSelect
    ref="input"
    :model-value="modelValue"
    :options="options"
    :label="label"
    :rules="rules"
    :error="!!errorMessages[errorKey]"
    :error-message="!!errorMessages[errorKey] ? errorMessages[errorKey] : ''"
    outlined
    option-label="fullName"
    option-value="id"
    emit-value
    map-options
    use-input
    hide-selected
    fill-input
    input-debounce="0"
    dense
    @filter="onFilter"
    @update:model-value="onInput"
  >
    <template #option="scope">
      <QItem v-bind="scope.itemProps">
        <UserCell v-model="scope.opt" />
      </QItem>
    </template>

    <template #no-option>
      <QItem>
        <QItemSection class="text-grey">
          Não existe este usuário
        </QItemSection>
      </QItem>
    </template>
  </QSelect>
</template>
