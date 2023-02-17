<template> 
    <v-app> 
        <TheTopNavbar />
        <v-main>
          <router-view></router-view>
        </v-main>
        <TheFooter />
    </v-app>
</template>

<script>



import TheTopNavbar from '@/components/TheTopNavbar.vue';
import djudService from '@/services/djudService';
import TheFooter from '@/components/TheFooter.vue';
import WebFontLoader from 'webfontloader'
export default {
  
  components: {
    TheTopNavbar,
    TheFooter,
  },

  created() {
      WebFontLoader.load({
        google: {
          families: [
            'Open Sans:300,400,500,600,700,800',
            'Roboto:100,300,400,500,700,900'
          ],
        },
        //active: this.setFontsLoaded(true)
      })
    },
    async mounted(){
      try {
        const result = await djudService.getDjudMsal()
      } catch (error) {
        console.log(error)
      }
    }
};

</script>

<style scoped>
.TheFooter{
  position:fixed
}
</style>