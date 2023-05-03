<script setup lang='ts'>
const attrs = useAttrs() as any
</script>

<template>
  <div>
    <div>
      Cálculo
    </div>
    <div>
      {{ attrs.id }}
    </div>
  </div>
</template>
