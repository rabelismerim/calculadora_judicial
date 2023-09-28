<script setup lang="ts">
const props = withDefaults(defineProps<{
  values?: any[]
  title?: string
  hint?: string
  labelKey?: string
  valueKeys?: string[]
}>(), {
  values: () => [],
  labelKey: 'label',
  valueKeys: () => ['count'],
})

const biggestValue = computed(() => [...clone(props.values)]
  .reduce((acc, curr: any) => {
    const values = Object.entries(curr)
      .filter(([key, value]) => props.valueKeys.includes(key) && typeof value === 'number')
      .map(([,value]) => value) as number[]
    const biggest = values
      .reduce((a, b) => (a > b) ? a : b, 0)
    return biggest > acc ? biggest : acc
  }, 0))
const biggestCaractersCount = computed(() => biggestValue.value.toFixed(2).length - 1)
</script>

<template>
  <div class="bg--base flex flex-col items-stretch gap-3 pt-4 pl-6 border-1 border-black/12 rounded-.5">
    <div v-if="title" class="flex no-wrap gap-3 items-start font-bold text-xl pr-6">
      {{ title }}
      <Hint :value="hint" class="mt-1.25" />
    </div>
    <div class="flex-1 flex flex-col justify-end">
      <div
        v-if="values.length < 1"
        class="flex items-center justify-center h-full"
      >
        Sem dados disponíveis...
      </div>
      <div
        v-else
        class="max-h-42 overflow-y-auto pr-6 pb-4"
      >
        <div
          class="grid gap-x-2 items-center"
          :style="{ gridTemplateColumns: `minmax(70px,1fr) 3fr ${Array(valueKeys.length).fill(`${biggestCaractersCount * 10}px`).join(' ')}` }"
        >
          <template v-if="valueKeys.length > 1">
            <div />
            <div />
            <div v-for="key in valueKeys" :key="key" class="font-bold text-xs text-center uppercase">
              {{ key }}
            </div>
          </template>
          <template
            v-for="item in values"
            :key="item[labelKey]"
          >
            <div class="overflow-hidden text-ellipsis whitespace-nowrap">
              {{ item[labelKey] }}
            </div>
            <div class="relative h-4 bg-gray-3 rounded-full overflow-hidden">
              <div
                v-for="(key, index) in valueKeys"
                :key="key"
                class="h-full absolute top-0 lef-0"
                :class="{
                  'bg--secondary ': index === 0,
                  'rounded-full': valueKeys.length === 1,
                }"
                :style="{
                  width: `${item[key] / (biggestValue || 1) * 100}%`,
                  zIndex: valueKeys.length - index,
                  backgroundColor: index > 0
                    ? `hsl(0,0%,${(1 - ((index === 1 && valueKeys.length === 2 ? 1 : index - 1) / Math.max(valueKeys.length - 2, 1))) * 30}%)`
                    : undefined,
                }"
              />
            </div>
            <div
              v-for="(valueKey, index) in valueKeys"
              :key="`${valueKeys[index]}-${valueKey}`"
              class="text-end font-bold"
              :class="{ 'cursor-pointer': item.valueHint }"
            >
              {{ item.digits ? formatNumber(item[valueKey], item.digits) : item[valueKey] }}
              <QTooltip v-if="item[`${valueKey}Hint`]">
                {{ item[`${valueKey}Hint`] }}
              </QTooltip>
            </div>
          </template>
        </div>
      </div>
    </div>
  </div>
</template>
