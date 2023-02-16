import store from '../store'
import router from '../router'

import axios from 'axios'

const apiCall = axios.create({
    baseURL: '/djud/api',
    // baseURL: 'https://uat.fadigitallab.deloitte.com.br/djud/api',
    withCredentials: true,
    xsrfHeaderName: 'X-CSRFToken',
    xsrfCookieName: 'csrftoken',
    timeout: 10000,
    hearders: { 
        Accept: 'application/json'
    }
})

// apiCall.getXSRFCookieValue = () => {
//     const cookies = decodeURIComponent(document.cookie).split('; ')
//     const xsrfCookieName = `${apiCall.defaults.xsrfCookieName}=`    
//     console.log(cookies,xsrfCookieName)
//     return cookies.find(c => c.startsWith(xsrfCookieName))?.replace(xsrfCookieName, '')
// }

const getCookie = (cookieName) => {
    const cookies = decodeURIComponent(document.cookie)
        .split(';')
        .map((item) => {
            const [name, value] = item.split('=')
            return {name, value}
        })
    return cookies.find(({name}) => name === cookieName)?.value
}

const setCookie = (cookieName, newvalue) => {
    
}

apiCall.getXSRFCookieValue = () => getCookie('xsrfCookieName')
console.log('COOKIE', getCookie('csrftoken'))

// TODO: Serviços com axios para cada tipo de uso axios services 
apiCall.interceptors.response.use(
    response => {

        return { 
            headers: response.headers, 
            data: response.data.data, 
            profile: response.data.profile 
        }

    }, 
    (error) => {
        console.warn(error);
    }
    // TODO: Fix error handling
    // error => {
    //     console.log( Promise.reject(error.response.data.data) )
    //     console.log(error.response.data.data)

    //     error.response.data = error.response.data.data

        
        
    //     //const { response, message } = error
        
    //     return error
    // }
        //let result = { error: 'UNKNOWN' }

    //     // backend error
    //     if (response) {                     
            
    //         if (response.status === 401 || response.status === 403) { // Forbidden
    //             result = {
    //                 error: 'SERVER_UNAUTHORIZED'
    //             }
    //         } else {
    //             result = {
    //                 error: 'SERVER_UNKNOWN'
    //             }
    //         }
        
    //     // network error
    //     } else if (message) {
    //         result = {
    //             error: 'NETWORK',
    //             message: message
    //         }
    //     }
        
    //     return result
    // }
)

export default apiCall