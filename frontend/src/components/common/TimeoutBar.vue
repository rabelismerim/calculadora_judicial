<script setup lang="ts">
const props = defineProps({
  timeout: {
    type: Number,
    default: Infinity,
  },
})

const bar = ref(null)

watchEffect(() => {
  if (bar.value === null)
    return
  if (props.timeout >= Infinity)
    return
  animate(bar.value, props.timeout * 1000,
    { transform: { scaleX: '100%' } },
    { transform: { scaleX: '0%' } })
})
</script>

<template>
  <div class="w-full h-1 rounded-.5 bg-black/10 overflow-hidden">
    <div
      ref="bar"
      class="w-full h-full origin-left bg-white/60"
    />
  </div>
</template>
