import Home from '@/views/home/Home.vue'

export default [
  { path: '/', 
  alias: ['/', '/home'],
  name: 'home', 
  component: Home },
  
  // { path: '/example', name: 'example', component: () => import('@/views/example/Example.vue'), },

  {
    path: '/login/:redirectPath',
    name: 'login',
    beforeEnter(to, from, next) {
      window.location.href = `${window.location.origin}/aplication/api/drfmsal_signin/aplication/`;
    },
    showInNav: false,
    authenticationRequired: false
  },
  {
    path: '/logout',
    name: 'logout',
    beforeEnter(to, from, next) {
      window.location.href = `${window.location.origin}/aplication/api/drfmsal_signout/aplication/`;
    },
    showInNav: false,
    authenticationRequired: false
  }
]