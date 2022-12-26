<template>
  <v-footer
    id="footer-nav"
    color="black"
    dark
    height="40"
    style="padding-bottom: 0px; padding-top:0px"
  >

      <v-col height="40px" style="padding-bottom: 0px;">
          <p style="font-size: 12px; margin: 0px; font-family: Open Sans;">© {{new Date().getFullYear()}} Para mais informações contate a Deloitte Global</p>
      </v-col>
  </v-footer>
</template>

<script>
  export default {
    name: 'NavFooter',

    data: () => ({
      links: [],
    }),
  }
</script>
