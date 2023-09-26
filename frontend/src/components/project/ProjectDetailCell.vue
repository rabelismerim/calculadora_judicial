<script setup lang="ts">
const props = withDefaults(defineProps<{
  label?: string
}>(),
{
})
</script>

<template>
  <div class="mb-5">
    <h3
      v-if="label"
      class="font-bold text--secondary uppercase leading-5 py-1"
    >
      {{ label }}
    </h3>
    <div>
      <slot />
    </div>
  </div>
</template>
