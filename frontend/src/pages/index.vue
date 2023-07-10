<script setup lang="ts">
const router = useRouter()

const { login } = $user

const inProduction = import.meta.env.PROD
const inDevelopment = import.meta.env.DEV
let isAuthenticated = $ref(false)

let loading = $ref(false)
let requested = $ref(false)

const enter = async () => {
  loading = true
  try {
    const { authorized, isActive } = await login()
    if (authorized || (inDevelopment && isActive)) {
      router.push({ path: '/projetos' })
    }
    else {
      requested = true
      loading = false
    }
  }
  catch (error) {
    printError('ERROR ON LOGIN:', error)
    loading = false
  }
}

onMounted(async () => {
  const { authenticated } = await usersService.verifyUser() || {}
  isAuthenticated = authenticated
})
</script>

<template>
  <div class="bg--base flex flex-1">
    <div class="flex flex-col-reverse pt-8 md:pt-0 pb-6 md:pb-0 md:grid md:grid-cols-2 md:gap-16 max-w-[min(1200px,100vw)] px-6 flex-1 mx-auto">
      <div class="flex flex-col justify-center gap-6">
        <h1 class="font-extrabold text-6xl mt-8">
          JUCA
        </h1>
        <h2 class="text-gray text-3xl">
          Sistema de Administração Judicial
        </h2>
        <p>
          <strong>JUCA</strong>, acrônimo de <strong>CÁ</strong>lculo <strong>JU</strong>dicial, é um sistema que simplifica os cálculos financeiros complexos no processo de administração judicial, fornecendo resultados precisos e confiáveis ao longo do tempo.
          <span class="hidden sm:block">Com sua interface amigável e algoritmos avançados, é a ferramenta ideal para advogados, analistas financeiros e demais profissionais envolvidos em processos de recuperação judicial e falência.</span>
        </p>
        <p>
          Para assitir o tutorial de uso da ferramenta <a href="https://becurious.edcast.eu/user/login" class="font-bold color--primary">Clique aqui</a>
        </p>
        <div class="flex flex-wrap gap-3">
          <div>
            <Btn
              v-if="!isAuthenticated && inProduction"
              label="Autenticar na Microsoft"
              loading-label="Enviando para a Microsoft..."
              :loading="loading"
              :disabled="requested"
              @click="enter"
            />
            <Btn
              v-else
              :label="!requested ? 'Entrar' : 'Pedido de acesso solicitado'"
              loading-label="Processando seus dados..."
              :loading="loading"
              :disabled="requested"
              @click="enter"
            />
          </div>
        </div>
      </div>
      <div class="px-8 flex justify-center">
        <Img :src="`${baseUrl}/illustrations/splash-balance.svg`" class="h-full min-h-10 min-w-50vw md:min-w-0" />
      </div>
    </div>
  </div>
</template>

<route lang="yaml">
meta:
  layout: splash
</route>
