<script setup lang="ts">
interface Link {
  label: string
  url?: string
}
const props = withDefaults(defineProps<{
  links: Link[]
}>(), {
  links: () => [],
})

const router = useRouter()
const filteredLinks = computed(() => props.links.filter(({ label }: any) => !!label))
</script>

<template>
  <div class="flex gap-1 items-center uppercase">
    <div
      v-if="links.length === 0"
      class="px-3 py-1 rounded-2 text--secondary font-bold"
    >
      Home
    </div>
    <div
      v-else
      class="px-3 py-1 rounded-2 hover:bg--secondary/20 text--content tween cursor-pointer"
      @click="router.push('/')"
    >
      Home
    </div>
    <div v-if="links.length > 0" class="i-carbon-chevron-right" />
    <template v-for="(link, index) in filteredLinks" :key="index">
      <div v-if="index < filteredLinks.length - 1" class="px-3 py-1 rounded-2 hover:bg--secondary/20 tween cursor-pointer" @click="router.push(link.url)">
        {{ link.label }}
      </div>
      <div v-else class="px-3 py-1 rounded-2 text--secondary font-bold">
        {{ link.label }}
      </div>
      <div v-if="index < filteredLinks.length - 1" class="i-carbon-chevron-right" />
    </template>
  </div>
</template>
