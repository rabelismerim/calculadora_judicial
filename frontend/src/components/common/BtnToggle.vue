<script setup lang='ts'>
interface Option {
  label: string
  value: string | boolean | number
}
const props = withDefaults(defineProps<{
  modelValue?: string | boolean | number
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
      class="rounded-0 border-none flex-1"
      type="button"
      @click="emit('update:model-value', button.value)"
    />
  </div>
</template>
