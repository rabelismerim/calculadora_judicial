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

const input = ref(null) as any
const hasError = computed(() => input.value.hasError)

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
    @update:model-value="(value: number) => emit('update:modelValue', value)"
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
