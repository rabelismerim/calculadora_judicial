<script setup lang='ts'>
interface Option {
  label: string
  value: string
}
const props = withDefaults(defineProps<{
  modelValue: string
  items: Option[]
  search?: string
}>(), {
  search: '',
})
const emit = defineEmits(['update:model-value', 'update:search'])
</script>

<template>
  <div class="mb-4 border-b-2 boder-black/12 flex justify-between items-center">
    <QTabs
      :model-value="modelValue"
      align="left"
      active-color="secondary"
      @update:model-value="value => emit('update:model-value', value)"
    >
      <QTab
        v-for="(tab, index) in items"
        :key="index"
        :name="tab.value"
        :label="tab.label"
      />
    </QTabs>
    <SearchFilter
      :model-value="search"
      @update:model-value="value => emit('update:search', value)"
    />
  </div>
</template>
