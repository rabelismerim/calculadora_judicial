<script setup lang="ts">
const emit = defineEmits(['notifyPendingUser'])

const router = useRouter()

const { login, user } = $user

const inProduction = import.meta.env.PROD
const inDevelopment = import.meta.env.DEV

let isLoading = $ref(false)
const requested = $ref(false)

const enter = async () => {
  const { authenticated, authorized, isActive } = user.value
  if ((inProduction && authenticated && authorized && isActive) || (inDevelopment && isActive))
    router.push({ path: '/projetos' })
  else
    emit('notifyPendingUser', { email: user.value.email })
}

let emailManagers = $ref([])
const emailBody = `Prezados,

Gostaria de solicitar formalmente acesso à aplicação Calculadora Judicial.
Por favor, conceda-me as permissões necessárias.
Agradeço antecipadamente pela sua atenção a esta solicitação.

Atenciosamente,

`.replaceAll('\n', '%0D%0A')
const mailto = computed(() => `mailto:${emailManagers.join(',')}?subject=Pedido de Acesso - Calculadora Judicial&body=${emailBody}`)

onMounted(async () => {
  isLoading = true
  try {
    await login()
    await delay(3)
    emailManagers = await usersService.getEmailManagers() || []
  }
  catch (error) {
    printError('ERROR ON LOGIN USER', error)
  }
  finally {
    isLoading = false
  }
})
</script>

<template>
  <div class="relative bg--base flex flex-1">
    <QLinearProgress
      v-if="isLoading"
      indeterminate
      color="secondary"
      class="absolute top-0 left-0"
      size="md"
    />
    <div class="flex flex-col-reverse pt-8 md:pt-0 pb-6 md:pb-0 md:grid md:grid-cols-2 md:gap-16 max-w-[min(1200px,100vw)] px-6 flex-1 mx-auto">
      <div class="flex flex-col justify-center gap-6">
        <h1 class="font-extrabold text-4xl sm:text-5xl lg:text-6xl mt-8">
          Calculadora Judicial
        </h1>
        <h2 class="text-gray text-3xl">
          Sistema de Administração Judicial
        </h2>
        <p>
          <strong>Calculadora Judicial</strong> é um sistema que simplifica os cálculos financeiros complexos no processo de administração judicial, fornecendo resultados precisos e confiáveis ao longo do tempo.
          <span class="hidden sm:block">Com sua interface amigável e algoritmos avançados, é a ferramenta ideal para advogados, analistas financeiros e demais profissionais envolvidos em processos de recuperação judicial e falência.</span>
        </p>
        <!-- <p>
          Para assitir o tutorial de uso da ferramenta <a href="https://becurious.edcast.eu/user/login" class="font-bold color--primary">Clique aqui</a>
        </p> -->
        <div class="flex flex-wrap gap-3">
          <div>
            <Btn
              v-if="!isLoading && user.authenticated && user.authorized && user.isActive"
              label="Entrar"
              @click="enter"
            />
            <Btn
              v-if="!isLoading && !user.isActive && inProduction"
              tag="a"
              :label="!requested ? 'Solicitar acesso' : 'Pedido de acesso solicitado'"
              :href="mailto"
              @click="requested = true"
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
