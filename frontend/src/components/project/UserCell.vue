<script setup lang="ts">
const props = withDefaults(defineProps<{
  modelValue: {
    name: string
    email: string
  }
}>(),
{
  modelValue: () => ({
    name: '',
    email: '',
  }),
})
</script>

<template>
  <div class="bg-secondary color-white h-10 w-10 flex justify-center items-center mr-3 font-bold">
    {{ getInitials(modelValue.name) }}
  </div>
  <div>
    <div class="font-bold">
      {{ modelValue.name }}
    </div>
    <div>
      {{ modelValue.email }}
    </div>
  </div>
</template>
