<template>
  <v-app-bar
    id="header-nav"
    app
    dark
    height="50"
    color="black"
    elevate-on-scroll
    class="pl-6 pr-6"
  >
  <meta name="viewport" content="width=device-width, initial-scale=1">  
    <div class="d-flex align-center">
      <router-link :to="{ name: 'home' }">
        <v-img
          alt="Deloitte"
          class="shrink mr-4 ml-0"
          contain
          src="@/assets/navbar/dtt_logo.png"
          transition="fade-transition"
          width="110"
        />
      </router-link>
    </div>

    <v-tabs
      class="ml-4"
    >
      <v-tabs-slider color=#86BC25 :style="[hideTabSlider ? {'width': '0'} : {'transition': '0.3s cubic-bezier(0.25, 0.8, 0.5, 1)'}]"></v-tabs-slider>
      <v-tab
        v-for="(link, i) in links"
        :key="i"
        :to="link.path"
      >
        {{ link.name }}
      </v-tab>
      <!-- <v-tab
        v-for="(link, i) in links"
        :key="i"
        :to="link.path"
        :style= "[i === 0 ? {'margin-bottom': '-20px'} : {}]"
      >
        <div v-if="i === 0" style="display:inline-block;">
          {{ link.name }}<br><i style="font-size:0.5rem;">(em construção)</i>
        </div>
        <template v-else>
          {{ link.name }}
        </template>
      </v-tab> -->
    </v-tabs>

    <v-spacer></v-spacer>

    <v-btn 
      small 
      text
      :to="log_status"
    >
      <v-avatar v-if="userProfile.authenticated" size="30" class="mr-2">
          <img v-if="userProfile.picture"
            :src="`data:image/jpeg;base64,${userProfile.picture}`"
          />
          <v-icon color="grey" v-else>{{ icons.accountCircle }}</v-icon>
        </v-avatar> {{ btnLoginText }} <v-icon class="ml-2">logout</v-icon>
    </v-btn>

    <v-divider
      class="mx-4"
      vertical
      inset
    ></v-divider>

    <div class="d-none d-md-block">
      <img alt="Analytics Logo" src="@/assets/navbar/analytics_logo.png" style="max-height: 27px;">
    </div>

    <v-divider
      class="mx-4"
      vertical
      inset
    ></v-divider>

    <div class="d-none d-sm-block">
      <img alt="App Logo" src="" style="max-height: 20px;">
    </div>
  </v-app-bar>
</template>

<script>
import { mapGetters } from 'vuex'

  export default {
    name: 'NavHeader',

    data: () => ({
      links: [
        {
          name: 'Home',
          path: '/'
        },
        // {
        //   name: 'exemplo',
        //   path: '/Exemplo'
        // },
      ]

    }),
    created() {
      const mainRoutes = this.$router.options.routes.find(r => { return r.name === "Main" })?.children
      if (mainRoutes)
        this.links = mainRoutes.flatMap((r) => (r.showInNav) ? [{name: r.name, path: r.path}] : [])
    },
    computed: {
      ...mapGetters('msal',{
    userProfile: 'userProfile',  
    // btnLoginText: 'userProfile.name' ? `Olá, ${userProfile.name}` : `Entrar`,
    // log_status: "userProfile.name ? '/logout' : `/login`"
  }
  ),
      // userProfile(){
      //   return this.$store.getters.userProfile
      // },
      hideTabSlider() {
        return this.$route.name === "home" || this.$route.name === "Engagement"
      },
      btnLoginText() {
        return this.userProfile.name ? `Olá, ${this.userProfile.name}` : `Entrar`
      },
      log_status() {
        return this.userProfile.name ? '/logout' : `/login`

      },
    },
    methods: {
      logout() {
        const vm = this;
        this.$store.dispatch('msal/AUTH_LOGOUT').then(async () => {
          await vm.$router.push({ name: 'home' });
        });
      },
      login() {
        const vm = this;
        this.$store.dispatch('msal/AUTH_LOGOUT').then(async () => {
          await vm.$router.push({ name: 'home' });
        });
      }
    }
  }
</script>
<style scoped>
    .v-tab{
      font-weight:600
    };
    .v-tab:hover, .v-tab--active{
      color: #86BC25
    };
    .v-tabs-slider{
      background-color: #86BC25
      };
</style>