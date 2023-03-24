<script setup lang='ts'>
interface Link {
  label: string
  url?: string
}
const props = withDefaults(defineProps<{
  menuLabel?: string
  loading?: boolean
  links?: Link[]
}>(), {
  menuLabel: 'Menu',
  links: () => [],
})
const router = useRouter()
const isOpen = $ref(false)
</script>

<template>
  <div>
    <div class="relative flex flex-1 justify-center">
      <QLinearProgress
        v-if="loading"
        indeterminate
        color="secondary"
        class="absolute top-0 left-0 z-1"
        size="md"
      />
      <div
        class="relative flex-1 grid tween-800"
        :class="{
          'lg:-translate-x-284px lg:w-[calc(100vw+284px)]': !isOpen && $slots.menu,
          'lg:grid-cols-[320px_1fr]': $slots.menu,
        }"
      >
        <div
          v-if="$slots.menu"
          class="fixed z-10 inset-block-0 pt-14 pb-10 left-0 max-w-80  lg:py-0 lg:relative bg--base pb-0 border-r-1 border-black/12 tween-800"
          :class="{ '-translate-x-284px lg:translate-0': !isOpen }"
        >
          <div class="relative pr-9 h-full max-h-[calc(100vh-96px)] overflow-x-hidden overflow-y-auto scroll-left">
            <div class="p-8 pr-0">
              <h2 class="font-bold text-2xl bg--base sticky top-0 py-4">
                {{ menuLabel }}
              </h2>
              <slot name="menu" />
            </div>
            <div
              class="absolute right-0 top-0 bottom-0 p-1 flex cursor-pointer"
              @click="isOpen = !isOpen"
            >
              <div class="hover:bg--secondary/15 pt-7 flex-1 flex flex-col items-center gap-4 rounded-2 tween">
                <div class="i-carbon-chevron-right text-lg tween-800" :class="{ 'rotate-180': isOpen }" />
                <div class="text-vertical whitespace-nowrap font-bold text-lg tween-800" :class="{ 'opacity-0': isOpen }">
                  {{ menuLabel }}
                </div>
              </div>
            </div>
          </div>
        </div>

        <div
          class="px-8 py-8 lg:pl-8 max-h-[calc(100vh-96px)] overflow-y-auto overflow-x-hidden flex justify-center"
          :class="{
            'pl-16': $slots.menu,
          }"
        >
          <div class="max-w-[min(1600px,100%)] w-full">
            <div class="flex gap-8 items-center mb-8">
              <button
                class="group flex gap-1 items-center uppercase font-semibold hover:text--secondary tween-800 z-1"
                @click="router.go(-1)"
              >
                <div class="i-carbon-chevron-left group-hover:-translate-x-1 tween-800" />
                Voltar
              </button>

              <Breadcrumbs v-if="links.length > 0" :links="links" />
            </div>
            <slot />
          </div>
        </div>
      </div>
    </div>
    <slot name="out" />
  </div>
</template>
