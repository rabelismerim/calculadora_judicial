<script setup lang='ts'>
interface Option {
  label: string
  value: string
}
const props = withDefaults(defineProps<{
  modelValue: string
  items: Option[]
}>(), {

})
const emit = defineEmits(['update:model-value'])
</script>

<template>
  <div class="flex no-wrap border-1 border--primary rounded-1 overflow-hidden">
    <Btn
      v-for="(button, index) in items"
      :key="index"
      :label="button.label"
      :transparent="modelValue !== button.value"
      :filled="modelValue === button.value"
      class="rounded-0 border-none"
      @click="emit('update:model-value', button.value)"
    />
  </div>
</template>
