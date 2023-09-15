<script setup lang="ts">
const props = withDefaults(defineProps<{
  types?: string[]
}>(), {

})
const emit = defineEmits(['drop'])

const dropZoneRef = ref(null)
const input = ref(null)
const onSelectFiles = (newFiles: File[] | null | Event) => {
  const files = Array.isArray(newFiles) ? newFiles : [...(input.value || { files: [] }).files]
  const filteredFiles = files
    .filter(({ name }) => (props.types?.length || 0) > 0
      ? props?.types?.some(type => name.endsWith(`.${type}`))
      : true)
  if (filteredFiles?.length === 0)
    return

  emit('drop', filteredFiles)
}
const { isOverDropZone } = useDropZone(dropZoneRef, onSelectFiles)
</script>

<template>
  <label ref="dropZoneRef" class="relative cursor-pointer flex flex-col w-full min-h-200px border-1 border-black/30 border-dashed justify-center items-center mt-6">
    <div class="flex flex-col gap-4 justify-center items-center">
      <div class="i-carbon-document-add text-5xl color-black/30" />
      <div>Clique ou jogue seus arquivos aqui!</div>
    </div>
    <input ref="input" type="file" multiple class="hidden" @change="onSelectFiles">
    <div v-if="isOverDropZone" class="absolute inset-0 bg--primary/20" />
  </label>
</template>
