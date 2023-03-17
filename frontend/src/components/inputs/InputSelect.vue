<script setup lang="ts">
import type { ValidationRule } from 'quasar'
import { printError } from '../../composables/utils'

const props = withDefaults(defineProps<{
  modelValue: any
  label?: string
  rules?: ValidationRule<any>[]
  options: any[]
  toAdd: Function
}>(), {
  rules: () => ([]),
  add: () => {},
  options: () => ([]),
})
const emit = defineEmits(['update:modelValue', 'update:options'])

const select = ref(null) as any
const hasError = computed(() => select.value.hasError)

let loading = $ref(false)
let inputValue = $ref('')
let filteredOptions = $ref(props.options)

const addNewItem = async () => {
  if (!inputValue) {
    throwError({
      message: 'Precisa de uma descrição para adicionar...',
    })
    return
  }
  loading = true
  try {
    const value = await props?.toAdd(inputValue)
    emit('update:options', [...props.options, value])
    // filteredOptions.push(value)
    inputValue = ''
    select.value.updateInputValue('', true)
    select.value.add(value)
  }
  catch (error) {
    printError(`ERROR ON ADD ITEM TO LIST ${props.label?.toUpperCase() || ''}:`, error)
  }
  finally {
    loading = false
  }
}

const onFilter = (val: any, update: Function) => {
  update(() => {
    const needle = val.toLowerCase()
    inputValue = needle
    filteredOptions = props.options
      .filter(v => v.description.toLowerCase().includes(needle))
  })
}
</script>

<template>
  <QSelect
    ref="select"
    :model-value="modelValue"
    :loading="loading"
    :options="filteredOptions"
    :label="label"
    :rules="rules"
    map-options
    option-value="id"
    option-label="description"
    outlined
    use-input
    hide-selected
    fill-input
    input-debounce="0"
    emit-value
    dense
    @filter="onFilter"
    @update:model-value="(value) => emit('update:modelValue', value)"
  >
    <template #no-option>
      <QBtn
        :label="`Adicionar${label ? ` ${label}` : ''}`"
        class="w-full h-12"
        color="primary"
        @click="addNewItem"
      >
        <div class="i-carbon-add-filled ml-3" />
      </QBtn>
    </template>
  </QSelect>
</template>
