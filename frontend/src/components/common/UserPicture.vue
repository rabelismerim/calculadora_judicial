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
  <div class="rounded-1 overflow-hidden">
    <Img
      v-if="modelValue.picture"
      :src="`data:image/jpeg;base64,${modelValue.picture}`"
      :error-image="`${baseUrl}/fallback/user.svg`"
      class="w-full h-full object-cover"
    />
    <div
      v-else
      class="bg-gray-2 rounded-.5 flex justify-center items-center text-[16px] h-full"
    >
      {{ getInitials(modelValue.fullName) }}
    </div>
  </div>
</template>
