<script setup lang="ts">
const props = withDefaults(defineProps<{
  modelValue: {
    fullName: string
    email: string
    picture?: string
  }
}>(),
{
  modelValue: () => ({
    fullName: '',
    email: '',
  }),
})
</script>

<template>
  <div class="flex items-center no-wrap gap-2 rounded-full pl-1 pr-3 py-1 border-1 border--primary/12 bg--primary/20 whitespace-nowrap">
    <UserPicture :model-value="modelValue" class="h-6 w-6 rounded-full" />
    <div class="font-bold">
      {{ modelValue.fullName }}
    </div>
    <QTooltip>
      {{ modelValue.email }}
    </QTooltip>
  </div>
</template>
