<script setup lang="ts">
const router = useRouter()

const { isAuthorized, login } = $user

const inProduction = import.meta.env.PROD

let loading = $ref(false)
let requested = $ref(false)

const enter = async () => {
  loading = true
  try {
    const user = await login()
    if (user?.isActive)
      router.push({ path: '/projetos' })
    else
      requested = true
  }
  catch (error) {
    printError('ERROR ON LOGIN:', error)
  }
  finally {
    loading = false
  }
}
</script>

<template>
  <div class="bg--base flex flex-1">
    <div class="grid sm:grid-cols-2 gap-16 max-w-[min(1200px,100vw)] px-6 flex-1 mx-auto">
      <div class="flex flex-col justify-center gap-6">
        <h1 class="font-extrabold text-6xl mt-8">
          JUCA
        </h1>
        <h2 class="text-gray text-3xl">
          Sistema de Administração Judicial
        </h2>
        <p>
          <strong>JUCA</strong>, acrônimo de <strong>CÁ</strong>lculo <strong>JU</strong>dicial, é um sistema que simplifica os cálculos financeiros complexos no processo de administração judicial, fornecendo resultados precisos e confiáveis ao longo do tempo. Com sua interface amigável e algoritmos avançados, é a ferramenta ideal para advogados, analistas financeiros e demais profissionais envolvidos em processos de recuperação judicial e falência.
        </p>
        <p>
          Para assitir o tutorial de uso da ferramenta <a href="https://becurious.edcast.eu/user/login" class="font-bold color--primary">Clique aqui</a>
        </p>
        <div class="flex flex-wrap gap-3">
          <div>
            <Btn
              v-if="!isAuthorized && inProduction"
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
      <div class="px-8">
        <Img :src="`${baseUrl}/illustrations/splash-balance.svg`" class="h-full min-h-10" />
      </div>
    </div>
  </div>
</template>

<route lang="yaml">
meta:
  layout: splash
</route>
