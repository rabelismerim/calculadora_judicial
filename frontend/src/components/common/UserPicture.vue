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
const userImage = computed(() => props.modelValue?.userpicture
  ? `data:image/jpg;base64,${props.modelValue?.userpicture}`
  : props.modelValue?.pictureUrl
    ? `${host}/juca${props.modelValue?.pictureUrl}`
    : undefined)
</script>

<template>
  <div class="rounded-1 overflow-hidden">
    <Img
      v-if="modelValue?.pictureUrl || modelValue?.userpicture"
      :src="userImage"
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
