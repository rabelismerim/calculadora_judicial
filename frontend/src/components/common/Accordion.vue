<script setup lang="ts">
const props = withDefaults(defineProps<{
  title?: string
  subtitle?: string
  summaryClass?: string
}>(), {
  title: '',
  subtitle: '',
})
const emit = defineEmits(['open', 'close'])

const details = ref(null) as any
const summary = ref(null) as any
const content = ref(null) as any

let isOpen = $ref(false)

const onToggle = () => {
  const wrapper = details.value
  const summaryHeight = summary.value.offsetHeight
  const contentHeight = content.value.offsetHeight
  const start = !isOpen ? summaryHeight : summaryHeight + contentHeight
  const end = !isOpen ? summaryHeight + contentHeight : summaryHeight
  const duration = -(0.999415 ** (contentHeight - 11800)) + 1220
  setStyle(wrapper, {
    overflow: 'hidden',
  })
  const animation = wrapper.animate({
    height: [`${start}px`, `${end}px`],
  }, {
    duration,
    easing: 'ease-in-out',
  })
  if (start < end) {
    isOpen = true
    emit('open')
  }
  animation.onfinish = () => {
    if (start > end) {
      isOpen = false
      emit('close')
    }
    wrapper.style.removeProperty('overflow')
  }
}
</script>

<template>
  <details
    ref="details"
    v-auto-animate
    :open="isOpen"
    class="bg--base text-left inline-block border-1 border-black/12 w-full rounded-.5"
  >
    <summary
      ref="summary"
      class="relative flex gap-4 cursor-pointer px-4 py-3 list-none box-border rounded-.5"
      :class="{ 'border-b-1 border-black/12': isOpen, [summaryClass || '']: summaryClass }"
      @click.prevent="onToggle"
    >
      <div class="flex items-center">
        <div class="w-8 h-8 rounded-full hover:bg--secondary/20 flex items-center justify-center tween">
          <div class="icon i-carbon-chevron-right w-6 h-6 text--secondary" />
        </div>
      </div>
      <slot name="header-left" />
      <div class="flex flex-col w-50 whitespace-nowrap">
        <div v-if="title" class="font-bold text-xl overflow-hidden text-ellipsis w-full">
          {{ title }}
        </div>
        <div v-if="subtitle" class="overflow-hidden text-ellipsis w-full">
          {{ subtitle }}
        </div>
      </div>
      <slot name="header-right" />
    </summary>
    <div
      ref="content"
      class="content"
    >
      <slot />
    </div>
  </details>
</template>

<style scoped>
summary .icon {
  transition: all .2s;
}
details[open] > summary .icon {
    transform: rotate(90deg);
}
</style>
