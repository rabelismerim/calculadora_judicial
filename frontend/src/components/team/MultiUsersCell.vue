<script setup lang='ts'>
const props = withDefaults(defineProps<{
  items: any[]
}>(),
{

})
</script>

<template>
  <div class="flex gap-2">
    <UserTag
      :model-value="items[0]"
    />
    <div class="flex items-center no-wrap rounded-full px-3 py-.5 border-1 border-gray/20 bg-gray/20 whitespace-nowrap cursor-help">
      + {{ items.length - 1 }}
      <QTooltip>
        <div class="flex max-w-100 justify-start items-center gap-2 ml-4 m-2">
          <UserTag
            v-for="(user, index) in items"
            :key="index"
            :model-value="user"
            transparent
          />
        </div>
      </QTooltip>
    </div>
  </div>
</template>
