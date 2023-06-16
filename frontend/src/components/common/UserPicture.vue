<script setup lang="ts">
const props = withDefaults(defineProps<{
  modelValue: {
    fullName: string
    email: string
    picture?: string
    userpicture?: string
  }
  initialsClass?: string
}>(),
{
  modelValue: () => ({
    fullName: '',
    email: '',
  }),
  initialsClass: '',
})
</script>

<template>
  <div class="rounded-1 overflow-hidden">
    <Img
      v-if="modelValue.picture || modelValue.userpicture"
      :src="`data:image/jpeg;base64,${modelValue.picture || modelValue.userpicture}`"
      :error-image="`${baseUrl}/fallback/user.svg`"
      class="w-full h-full object-cover"
    />
    <div
      v-else
      class="bg-gray-2 rounded-.5 flex justify-center color-slate-6 items-center text-[16px] h-full"
      :class="initialsClass"
    >
      {{ getInitials(modelValue.fullName) }}
    </div>
  </div>
</template>
