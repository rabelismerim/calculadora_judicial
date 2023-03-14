<script setup lang="ts">
const props = withDefaults(defineProps<{
  modelValue: boolean
  title?: string
  hint?: string
  modalClass?: string
  closeDisabled?: boolean
}>(), {
  modelValue: false,
  modalClass: '',
})
const emit = defineEmits(['update:modelValue', 'close'])
const close = () => {
  emit('update:modelValue', false)
  emit('close')
}
</script>

<template>
  <div
    class="fixed inset-0 flex justify-center items-center bg-black/20 z-1000 with-transition"
    :class="{
      'opacity-100 pointer-events-auto': modelValue,
      'opacity-0 pointer-events-none': !modelValue,
    }"
  >
    <div
      class="relative bg--base w-full m-4 max-h-[calc(100vh-32px)] rounded-.5 border-1 border-black/28 with-transition"
      :class="{
        'translate-y-10': !modelValue,
        'max-w-240': !modalClass,
        [modalClass]: modalClass,
      }"
    >
      <div class="flex gap-2 p-4 mb-1">
        <div class="flex-1 flex items-center gap-3">
          <span class="font-bold text-2xl">{{ title }}</span>
          <Hint :value="hint" />
        </div>
        <button
          :disabled="closeDisabled"
          class="h-8 w-8 flex justify-center items-center text-lg rounded-full bg-black/6 hover:bg-black/12 with-transition"
          @click="close"
        >
          <div class="i-carbon-close" />
        </button>
      </div>
      <slot />
    </div>
  </div>
</template>
