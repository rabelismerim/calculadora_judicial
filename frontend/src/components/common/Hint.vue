<script setup lang="ts">
const props = withDefaults(defineProps<{
  value: String
}>(), {
})
</script>

<template>
  <div v-if="value" class="cursor-help text-base">
    <div class="i-carbon-help-filled mt-1 color-black/30 hover:color--primary with-transition" />
    <QTooltip>{{ value }}</QTooltip>
  </div>
</template>
