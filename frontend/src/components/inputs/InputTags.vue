<script setup lang="ts">
import type { ValidationRule } from 'quasar'
const props = withDefaults(defineProps<{
  modelValue: string[]
  label?: string
  rules?: ValidationRule<any>[]
  errorMessages?: any
  errorKey?: string
}>(), {
  rules: () => ([]),
  errorMessages: () => ({}),
  errorKey: '',
})
const emit = defineEmits(['update:modelValue'])

const input = ref(null as any)
const inputcontent = ref(null as any)
const inputvalue = ref(null as any)

let localValue: string[] = $ref([])
watchEffect(() => {
  localValue = props.modelValue
})

const hasError = computed(() => input.value.hasError)
const { clearError } = useBackendErrors(toRef(props, 'errorMessages'))
const clearErrors = () => {
  if (props.errorKey)
    clearError(props.errorKey)
}

const updateValue = () => {
  clearErrors()
  emit('update:modelValue', clone(localValue))
}
const clear = () => {
  clearErrors()
  emit('update:modelValue', [])
}

let inputValue = $ref('')
let itemEditing = $ref(-1)
const editTag = async (index: number) => {
  itemEditing = index
  await delay(0.1)
  if (inputcontent.value[0])
    inputcontent.value[0].focus()
}
const add = () => {
  if (!inputValue)
    return
  localValue.push(inputValue)
  inputValue = ''
  updateValue()
}
const remove = (index: number) => {
  localValue.splice(index, 1)
  updateValue()
}
const updateItem = (event: Event, index: number) => {
  const target = event.target as HTMLInputElement
  localValue[index] = target?.value || ''
  updateValue()
}

const onFocus = () => {
  nextTick(() => inputvalue.value.focus())
}
const onBlur = () => {
  if (inputValue)
    localValue.push(inputValue.toUpperCase())
  inputValue = ''
  itemEditing = -1
}

const getContentSize = (content: string) => {
  const div = createEl('span')
  div.innerText = content
  setStyle(div, {
    whiteSpace: 'pre',
  })
  document.body.appendChild(div)
  const { width } = div.getBoundingClientRect()
  document.body.removeChild(div)
  return width
}
</script>

<template>
  <QField
    ref="input"
    :model-value="localValue"
    :label="label"
    :rules="rules"
    :error="!!errorMessages[errorKey]"
    :error-message="!!errorMessages[errorKey] ? errorMessages[errorKey] : ''"
    dense
    outlined
    tabindex="0"
    @update:model-value="updateValue"
    @blur="onBlur"
    @focus="onFocus"
  >
    <template #control="{ id, floatingLabel }">
      <div class="flex gap-1 w-full pt-1.5 pb-1 pr-8">
        <div
          v-for="(item, index) in localValue"
          :key="index"
          class="max-w-fill flex items-center no-wrap gap-2 rounded-full pl-3 pr-1 py-1 border-1 border--primary/12 whitespace-nowrap max-w-fill tween cursor-pointer"
          :class="{
            'bg--primary color-white': itemEditing === index,
            'bg--primary/20 color-inherit': itemEditing !== index,
          }"
          @click.stop="editTag(index)"
        >
          <input
            v-if="itemEditing === index"
            ref="inputcontent"
            :value="localValue[index]"
            class="bg-transparent outline-none max-w-fill"
            :style="{
              width: `${getContentSize(localValue[index])}px`,
            }"
            oninput="this.value = this.value.toUpperCase()"
            @input="updateItem($event, index)"
            @blur="itemEditing = -1"
          >
          <div
            v-else
            class="bg-transparent flex-1 text-ellipsis overflow-hidden"
          >
            <span class="whitespace-pre">{{ item }}</span>
          </div>
          <div
            class="rounded-full bg-white/20 hover:bg-white/50 min-h-5 min-w-5 flex justify-center items-center cursor-pointer"
            @click.stop="remove(index)"
          >
            <div class="i-carbon-close" />
          </div>
        </div>
        <input
          v-show="floatingLabel && itemEditing === -1"
          :id="id"
          ref="inputvalue"
          v-model="inputValue"
          class="bg-transparent outline-none flex-1 min-w-8"
          oninput="this.value = this.value.toUpperCase()"
          @keyup.enter="add"
          @focus="inputValue = ''; itemEditing = -1"
        >
      </div>
      <div class="group-hover:opacity-100 group-hover:pointer-events-auto absolute -right-.5 top-50% -translate-y-50%">
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
          class="h-8 w-8 rounded-full bg-black/12 hover:bg--error hover:color-white flex justify-center items-center cursor-pointer tween"
          @dblclick.stop="clear"
        >
          <div class="i-carbon-trash-can" />
          <QTooltip>Para limpar todos os itens use um click duplo</QTooltip>
        </div>
      </div>
    </template>
  </QField>
</template>
