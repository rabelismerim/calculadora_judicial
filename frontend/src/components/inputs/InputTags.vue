<script setup lang="ts">
const props = withDefaults(defineProps<{
  modelValue: string[]
  label?: string
}>(), {
  modelValue: () => ([]),
})
const emit = defineEmits(['update:modelValue'])

let inputValue = $ref('')
const itemEditing = $ref(-1)
const add = () => {
  const items = [...props.modelValue]
  items.push(inputValue)
  inputValue = ''
  emit('update:modelValue', items)
}
const remove = (index: number) => {
  const items = [...props.modelValue]
  items.splice(index, 1)
  emit('update:modelValue', items)
}
const clear = () => {
  emit('update:modelValue', [])
}
const updateItem = (event: Event, index: number) => {
  const target = event.target as HTMLInputElement
  const items = [...props.modelValue]
  items[index] = target?.value || ''
  emit('update:modelValue', items)
}
</script>

<template>
  <label
    class="relative overflow-hidden block group ring-1 ring-inner ring-black/24 hover:ring-black focus-within:hover:ring--primary focus-within:ring--primary focus-within:ring-2 rounded-1 py-1.5 pl-2.5 pr-10 min-h-14 with-transition"
    @click.self.stop="itemEditing = -1"
  >
    <span
      v-if="label"
      class="text-xs inline-block max-w-74% origin-top-left color-black/60 group-focus-within:text--primary whitespace-nowrap overflow-hidden text-ellipsis with-transition"
      :class="{
        'scale-133 translate-y-2.8 group-focus-within:max-w-100% group-focus-within:scale-100 group-focus-within:translate-y-0': modelValue.length <= 0,
        'scale-100 translate-y-0': modelValue.length > 0,
      }"
    >
      {{ label }}
    </span>
    <div
      v-auto-animate
      class="flex gap-1"
      :class="{
        'pt-1': modelValue.length > 0,
      }"
    >
      <div
        v-for="(item, index) in modelValue"
        :key="index"
        class="max-w-fill flex items-center no-wrap gap-2 rounded-full pl-3 pr-1 py-1 border-1 border--primary/12 whitespace-nowrap max-w-fill with-transition"
        :class="{
          'bg--primary color-white': itemEditing === index,
          'bg--primary/20 color-inherit': itemEditing !== index,
        }"
        @click.stop="itemEditing = index"
      >
        <input
          v-if="itemEditing === index"
          :value="modelValue[index]"
          class="bg-transparent outline-none max-w-fill"
          :style="{
            width: `${item.length}ch`,
          }"
          @input="updateItem($event, index)"
          @blur="itemEditing = -1"
        >
        <div
          v-else
          class="bg-transparent flex-1 text-ellipsis overflow-hidden"
        >
          {{ item }}
        </div>
        <div
          class="rounded-full bg-white/20 hover:bg-white/50 min-h-5 min-w-5 flex justify-center items-center cursor-pointer"
          @click.stop="remove(index)"
        >
          <div class="i-carbon-close" />
        </div>
      </div>
      <input
        v-model="inputValue"
        class="opacity-0 absolute pointer-events-none bg-transparent outline-none flex-1 min-w-8"
        :class="{
          'group-focus-within:opacity-100 group-focus-within:relative group-focus-within:pointer-events-auto': itemEditing === -1,
        }"
        @keyup.enter="add"
        @focus="inputValue = ''; itemEditing = -1"
      >
    </div>
    <div class="opacity-0 pointer-events-none group-hover:opacity-100 group-hover:pointer-events-auto absolute right-2 top-50% -translate-y-50%">
      <div
        v-if="inputValue.length > 0 ? true : undefined"
        class="h-8 w-8 rounded-full bg--primary/80 hover:bg--primary  flex justify-center items-center color-white text-lg cursor-pointer"
        @click.stop="add"
      >
        <div class="i-carbon-add" />
        <QTooltip>Adicionar novo item</QTooltip>
      </div>
      <div
        v-else-if="modelValue.length > 0"
        class="h-8 w-8 rounded-full bg-black/12 hover:bg-red hover:color-white flex justify-center items-center cursor-pointer with-transition"
        @dblclick.stop="clear"
      >
        <div class="i-carbon-trash-can" />
        <QTooltip>Para limpar todos os itens use um click duplo</QTooltip>
      </div>
    </div>
  </label>
</template>
