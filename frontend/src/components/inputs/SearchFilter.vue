<script setup lang="ts">
const props = withDefaults(defineProps<{
  search?: string
  field?: string
  options?: any
  hint?: string
}>(), {
  search: '',
  options: () => ({}),
})
const emit = defineEmits(['update:search', 'update:field', 'clear'])

let localSearch = $ref(props.search)
watchEffect(() => {
  localSearch = props.search
})
const menuOptions = $computed(() => Object.entries(props.options)
  .map(([value, label]) => ({ label, value })))

const input = ref()
const menu = ref()
let showMenu = $ref(false)
onClickOutside(menu, () => showMenu = false)

const clear = () => {
  localSearch = ''
  emit('update:search', '')
  emit('clear')
}

const updateSearch = () => emit('update:search', localSearch)
const updateField = async (value: string) => {
  showMenu = false
  emit('update:field', value)
  await delay(0.1)
  input.value.focus()
}
</script>

<template>
  <div
    :class="[search ? 'outline--secondary' : 'focus-within:outline--primary']"
    class="relative flex flex-nowrap rounded-.5"
    @click.stop
  >
    <button
      class="relative bg--base pl-3 pr-2 border-y-1 border-l-1 rounded-l-.5 border--content/12 flex flex-nowrap gap-2 items-center tween"
      :class="{ 'bg--secondary text--base': search }"
      @click.stop="showMenu = true"
    >
      <div class="i-carbon-search" />
      <div>{{ options?.[field as string] ?? '' }}</div>
      <div
        class="i-carbon-chevron-down tween"
        :class="{ 'rotate-180': showMenu }"
      />
      <div
        v-show="showMenu"
        ref="menu"
        class="absolute bottom-0 -right-1px w-[calc(100%+2px)] translate-y-100% z-100 shadow-2xl flex flex-col rounded-1 overflow-hidden bg--base border-1 border--content/12 min-w-[max-content]"
      >
        <button
          v-for="({ label, value }, index) in menuOptions"
          :key="index"
          class="hover:bg--primary/12 py-3 px-5 tween"
          :class="{ 'bg--primary/50!': value === field }"
          @click.stop="updateField(value)"
        >
          {{ label }}
        </button>
      </div>
    </button>
    <label
      class="input-sizer inline-grid align-top items-center bg--base pl-2 pr-10 border-1 border--content/12 rounded-r-.5 max-w-[calc(var(--w)+3rem)]"
      style="--w: 15rem;"
      :data-value="localSearch"
    >
      <input
        ref="input"
        v-model="localSearch"
        type="text"
        size="5"
        placeholder="buscar..."
        class="outline-none max-w-[var(--w)] h-10 py-1"
        @input="debounce(updateSearch)"
      >
    </label>
    <button
      v-if="search?.length > 0"
      class="group absolute right-1 flex justify-center items-center top-50% -translate-y-50% h-8 w-8 rounded-.5 hover:bg--error tween"
      @click="clear"
    >
      <div class="i-carbon-close text-lg group-hover:text-white" />
    </button>
  </div>
</template>

<style>
.input-sizer::after,
.input-sizer input {
  width: auto;
  min-width: 1em;
  grid-area: 1/2;
  font: inherit;
  margin: 0;
  resize: none;
}
.input-sizer::after {
  content: attr(data-value) " ";
  visibility: hidden;
  white-space: pre-wrap;
}
</style>
