<script setup lang="ts">
const props = withDefaults(defineProps<{
  modelValue?: boolean
  title?: string
  hint?: string
  modalClass?: string
  closeDisabled?: boolean
  loading?: boolean
}>(), {
  modelValue: false,
  modalClass: '',
})
const emit = defineEmits(['update:model-value', 'close'])
const close = () => {
  emit('update:model-value', false)
  emit('close')
}
</script>

<template>
  <div
    class="fixed inset-0 flex justify-center items-center bg-black/20 z-1000 tween"
    :class="{
      'opacity-100 pointer-events-auto': modelValue,
      'opacity-0 pointer-events-none': !modelValue,
    }"
  >
    <div
      class="relative bg--base w-full m-4 max-h-[calc(100vh-32px)] rounded-.5 border-1 border-black/28 tween"
      :class="{
        'translate-y-10': !modelValue,
        'max-w-240': !modalClass,
        [modalClass]: modalClass,
      }"
    >
      <div class="flex gap-2 p-4 pb-5 relative">
        <div class="flex-1 flex items-center gap-3">
          <span class="font-bold text-2xl">{{ title }}</span>
          <Hint :value="hint" />
        </div>
        <button
          :disabled="closeDisabled"
          class="h-8 w-8 flex justify-center items-center text-lg rounded-full bg-black/6 hover:bg-black/12 tween"
          @click="close"
        >
          <div class="i-carbon-close" />
        </button>
        <QLinearProgress
          v-if="loading"
          indeterminate
          color="secondary"
          class="absolute bottom-0 left-0"
          size="xs"
        />
      </div>
      <slot />
    </div>
  </div>
</template>
