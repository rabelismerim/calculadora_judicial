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
  <div class="mr-3">
    <UserPicture :model-value="modelValue" class="h-10 w-10" />
  </div>
  <div>
    <div class="font-bold">
      {{ modelValue.fullName }}
    </div>
    <div>
      {{ modelValue.email }}
    </div>
  </div>
</template>
