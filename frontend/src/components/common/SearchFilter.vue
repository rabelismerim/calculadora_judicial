<script setup lang="ts">
const props = withDefaults(defineProps<{
  modelValue: String
  label?: string
  hint?: string
}>(), {
  label: 'Buscar',
})
const emit = defineEmits(['update:modelValue', 'clear'])

const onInput = (event: Event) => {
  const target = event.target as HTMLInputElement
  emit('update:modelValue', target?.value)
}
const clear = () => {
  emit('update:modelValue', '')
  emit('clear')
}
</script>

<template>
  <label class="relative">
    <span class="mr-4">{{ label }}</span>
    <input
      :value="modelValue"
      type="text"
      class="border-1 border-black/12 py-1 pl-1 pr-10 rounded-.5 h-10"
      @input="onInput"
    >
    <button
      v-if="modelValue.length > 0"
      class="group absolute right-1 flex justify-center items-center top-50% -translate-y-50% h-8 w-8 rounded-.5 hover:bg--primary transition duration-300 ease-in-out"
      @click="clear"
    >
      <div class="i-carbon-close text-lg group-hover:text-white" />
    </button>
    <div v-else class="i-carbon-search absolute right-3 top-50% -translate-y-50%" />
  </label>
</template>
