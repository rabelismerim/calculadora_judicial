<script setup lang='ts'>
interface Option {
  label: string
  value: string
}
const props = withDefaults(defineProps<{
  modelValue: string | number
  items: Option[] | any[]
  search?: string
}>(), {
})
const emit = defineEmits(['update:model-value', 'update:search'])
</script>

<template>
  <div class="mb-4 border-b-2 boder-black/12 flex justify-between items-center">
    <QTabs
      :model-value="modelValue"
      align="left"
      active-color="secondary"
      @update:model-value="(value: any) => emit('update:model-value', value)"
    >
      <QTab
        v-for="(tab, index) in items"
        :key="index"
        :name="tab.value"
        :label="tab.label"
        @click="() => tab?.onclick?.()"
      />
    </QTabs>
    <div v-if="$slots.side">
      <slot name="side" />
    </div>
    <SearchFilter
      v-else-if="search !== undefined"
      :search="search"
      @update:search="(value: any) => emit('update:search', value)"
    />
  </div>
</template>
