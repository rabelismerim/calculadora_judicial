<script setup lang="ts">
const router = useRouter()

let loading = $ref(false)
const enter = async () => {
  router.push({ path: '/projetos' })
}
const { isAuthenticated, hasPermission } = $user
const login = async () => {
  loading = true
  try {
    await $user.login()
  }
  catch (error) {
    console.warn('ERROR ON LOGIN:', error)
  }
  finally {
    loading = false
  }
}
</script>

<template>
  <div class="bg--base flex flex-1">
    <div class="grid sm:grid-cols-2 gap-16 max-w-300 px-6 flex-1 mx-auto">
      <div class="flex flex-col justify-center gap-6">
        <h1 class="font-extrabold text-6xl mt-8">
          JUCA
        </h1>
        <h2 class="text-gray text-3xl">
          Sistema de Recuperação Financeira
        </h2>
        <p>
          <strong>JUCA</strong>, acrônimo de <strong>CÁ</strong>lculo <strong>JU</strong>dicial, é um sistema que simplifica os cálculos financeiros complexos necessários nessas operações, fornecendo resultados precisos e confiáveis ao longo do tempo. Com sua interface amigável e algoritmos avançados, é a ferramenta ideal para advogados, analistas financeiros e demais profissionais envolvidos em processos de recuperação judicial e falência.
          <!-- Para assistir ao tutorial de uso da ferramenta Clique aqui -->
        </p>
        <div class="flex flex-wrap gap-3">
          <Btn
            v-if="getCookie('csrftoken')"
            label="Entrar"
            @click="enter"
          />
          <Btn
            v-else-if="!isAuthenticated"
            label="Entrar"
            @click="login"
          />
          <Btn
            v-else-if="!hasPermission"
            color="secondary"
            label="Solicitar acesso"
            loading-label="enviando Solicitação..."
            :loading="loading"
            @click="loading = !loading"
          />
        </div>
      </div>
      <div class="px-8">
        <Img src="/illustrations/splash-balance.svg" class="h-full min-h-10" />
      </div>
    </div>
  </div>
</template>

<route lang="yaml">
meta:
  layout: splash
</route>
