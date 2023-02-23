<script setup lang="ts">
const router = useRouter()
</script>

<template>
  <NavBar show-exit>
    <Btn
      label="Home"
      grow
      transparent
      color="white"
      @click="router.push({ path: '/' })"
    />
    <Btn
      label="Projetos"
      grow
      transparent
      color="secondary"
      @click="router.push({ path: '/projetos' })"
    />
    <Btn
      label="Time"
      grow
      transparent
      color="white"
      disabled
      @click="router.push({ path: '/time' })"
    />
    <Btn
      label="Atividades"
      grow
      transparent
      color="white"
      disabled
      @click="router.push({ path: '/atividades' })"
    />
  </NavBar>
  <div class="flex flex-1 flex-col">
    <RouterView />
  </div>
  <FooterBar />
</template>
