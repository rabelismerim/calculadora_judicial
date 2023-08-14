<script setup lang="ts">
const props = withDefaults(defineProps<{
  modelValue: {
    fullName: string
    email: string
    pictureUrl?: string
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

const host = import.meta.env.VITE_API_HOST
const userImage = computed(() => `${host}/juca${props.modelValue?.pictureUrl}`)
</script>

<template>
  <div class="rounded-1 overflow-hidden">
    <Img
      v-if="modelValue?.pictureUrl"
      :src="`${host}/juca${props.modelValue?.pictureUrl}`"
      class="w-full h-full object-cover"
      :error-image="`${baseUrl}/fallback/user.svg`"
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
