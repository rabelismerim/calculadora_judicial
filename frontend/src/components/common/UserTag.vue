<script setup lang="ts">
const props = withDefaults(defineProps<{
  modelValue: {
    fullName: string
    email: string
    picture?: string
  }
  transparent?: boolean
}>(),
{
  modelValue: () => ({
    fullName: '',
    email: '',
  }),
})
</script>

<template>
  <div
    class="flex items-center no-wrap gap-2 rounded-full pl-.5 pr-3 py-.5 whitespace-nowrap cursor-help"
    :class="{ 'border-1 border-gray/20 bg-gray/20': !transparent }"
  >
    <UserPicture :model-value="modelValue" class="h-5 w-5 rounded-full" initials-class="text-[9px] font-bold" />
    <div class="font-bold">
      {{ modelValue.fullName }}
    </div>
    <QTooltip>
      <div class="flex flex-col gap-2 text-sm pt-2 justify-center items-center">
        <UserPicture :model-value="modelValue" class="h-16 w-16 rounded-1" />
        <div class="font-bold">
          {{ modelValue.fullName }}
        </div>
        <div>{{ modelValue.email }}</div>
      </div>
    </QTooltip>
  </div>
</template>
