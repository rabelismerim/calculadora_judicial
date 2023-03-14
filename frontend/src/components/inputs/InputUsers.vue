<script setup lang="ts">
import type { ValidationRule } from 'quasar'
const props = withDefaults(defineProps<{
  modelValue: any
  label?: string
  rules?: ValidationRule<any>[]
  users?: any[]
}>(), {
  rules: () => ([]),
  users: () => ([]),
})
const emit = defineEmits(['update:modelValue'])

const input = ref(null) as any
const hasError = computed(() => input.value.hasError)

let options = $ref(props.users)
const onFilter = (val: string, update: any) => {
  update(() => {
    const needle = val.toLowerCase()
    options = props.users.filter(({ name }) =>
      name.toLowerCase().includes(needle),
    )
  })
}
</script>

<template>
  <QSelect
    ref="input"
    :model-value="modelValue"
    :options="options"
    :label="label"
    :rules="rules"
    outlined
    option-label="name"
    option-value="id"
    emit-value
    map-options
    use-input
    fill-input
    input-debounce="0"
    multiple
    use-chips
    @filter="onFilter"
    @update:model-value="(value: number) => emit('update:modelValue', value)"
  >
    <template #selected-item="scope">
      <div class="max-w-fill mt-1.5 mr-1.5 flex items-center no-wrap gap-2 rounded-full pl-1 pr-1 py-1 border-1 border--primary/12 whitespace-nowrap max-w-fill with-transition bg--primary/20 color-inherit">
        <div class="bg-transparent flex nowrap items-center flex-1 text-ellipsis overflow-hidden">
          <UserPicture :model-value="scope.opt" class="h-6 w-6 rounded-full mr-2" />
          <span class="whitespace-pre">{{ scope.opt.name }}</span>
        </div>
        <div
          class="rounded-full bg-white/20 hover:bg-white/50 min-h-5 min-w-5 flex justify-center items-center cursor-pointer"
          @click="scope.removeAtIndex(scope.index)"
        >
          <div class="i-carbon-close" />
        </div>
      </div>
    </template>

    <template #option="scope">
      <QItem v-bind="scope.itemProps">
        <UserCell v-model="scope.opt" />
      </QItem>
    </template>

    <template #no-option>
      <QItem>
        <QItemSection class="text-grey">
          Não existe este usuário
        </QItemSection>
      </QItem>
    </template>
  </QSelect>
</template>
