import Vue from 'vue'
import Vuex from 'vuex'

export const AUTH_LOGIN_MSAL = "AUTH_LOGIN_MSAL"
export const AUTH_LOGIN = "AUTH_LOGIN"
export const AUTH_LOGOUT = "AUTH_LOGOUT"

const state = () => ({
    // user info
    userMSALAuthenticated: false,
    userAuthenticatedLast: false,
    userAuthenticated: false,
    userName: null,
    userPicture: null,
  })
  
  // getters
  const getters = {
    userProfile: (s) => {
        return {
            msalAuthenticated: s.userMSALAuthenticated,
            authenticatedLast: s.userAuthenticatedLast,
            authenticated: s.userAuthenticated,
            name: s.userName,
            picture: s.userPicture
        }
        },
  }
  
  // actions
  const actions = {
    profileCheck: ({ commit }) => new Promise((resolve) => {
        Vue.prototype.$http.get('/drfmsal_signstatus')
            .then((response) => {
            if (!Object.prototype.hasOwnProperty.call(response, 'error')) {
                commit('setUserProfile', response.data.profile)
                resolve(true)
            } else {
                commit('unsetUserProfile')
                resolve(false)
            }
            })
        }),
  }
  
  // mutations
  const mutations = {
    [AUTH_LOGIN]: (state, payload) => {
        localStorage.setItem("bhd-username", payload)
        localStorage.setItem("bhd-authenticated", true)
        state.authIsAuthenticated = true
        state.authName = payload
        state.authError = ""
      },
      [AUTH_LOGOUT]: (state) => {
        localStorage.removeItem("bhd-username")
        localStorage.removeItem("bhd-authenticated")
        state.authIsAuthenticated = false
        state.authName = ""
        state.authError = ""
      },

      initialiseStore: (state) => {
        const bhdUsername = localStorage.getItem("bhd-username")
        const bhdAuthenticated = localStorage.getItem("bhd-authenticated")
        if (bhdUsername && bhdAuthenticated) {
          state.authIsAuthenticated = true
          state.authName = bhdUsername
          state.authError = ""
        }      
      },
  
      setUserProfile: (state, payload) => {
        state.userMSALAuthenticated = payload.authenticated
        state.userAuthenticatedLast = state.userAuthenticated
        state.userAuthenticated = payload.authorized
        state.userName = payload.user_fullname
        state.userPicture = payload.user_picture
      },
      unsetUserProfile: (state) => {
        state.userMSALAuthenticated = false
        state.userAuthenticatedLast = state.userAuthenticated
        state.userAuthenticated = false
        state.userName = null
        state.userPicture = null
      },
  }
  
  export default {
    namespaced: true,
    state,
    getters,
    actions,
    mutations
  }