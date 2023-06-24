<script setup lang='ts'>
const props = withDefaults(defineProps<{
  modelValue: number
  disabled?: boolean
}>(), {
})
const emit = defineEmits(['update:modelValue', 'addLines'])

const onInput = (event: Event) => {
  const { target } = event as any
  const toEmit = (+target?.value < 1) ? 1 : +target?.value
  emit('update:modelValue', toEmit)
}
const add = () => {
  emit('update:modelValue', props.modelValue + 1)
}
const subtract = () => {
  if (props.modelValue > 1)
    emit('update:modelValue', props.modelValue - 1)
}
const onAddLines = () => {
  emit('addLines')
}
</script>

<template>
  <Btn
    label="Adicionar Linhas"
    icon="i-carbon-add-filled"
    type="button"
    transparent
    :disabled="disabled"
  >
    <QMenu anchor="bottom right" self="top right">
      <div class="flex flex-col p-2 gap-2">
        <div class="flex gap-2 no-wrap">
          <button
            class="p-2 color--primary hover:bg--primary/12 rounded"
            @click="subtract"
          >
            <div class="i-carbon-subtract" />
          </button>
          <input
            :value="modelValue"
            type="number"
            step="1"
            min="1"
            class="max-w-26 px-2 text-center focus:outline--primary"
            @input="onInput"
            @keypress="(['-', '.'].includes($event.key)) && $event.preventDefault()"
          >
          <button
            class="p-2 color--primary hover:bg--primary/12 rounded"
            @click="add"
          >
            <div class="i-carbon-add" />
          </button>
        </div>
        <button
          v-close-popup class="px-4 py-2 rounded text-center color--primary bg--primary/12 hover:bg--primary hover:color-white"
          @click="onAddLines"
        >
          Adicionar Linhas
        </button>
      </div>
    </QMenu>
  </Btn>
</template>
