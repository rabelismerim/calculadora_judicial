import store from '../store'
import router from '../router'

import axios from 'axios'

const apiCall = axios.create({
    baseURL: 'https://brdcvmdev07/djud/api',
    withCredentials: true,
    xsrfHeaderName: 'X-CSRFToken',
    xsrfCookieName: 'csrftoken',
    timeout: 10000
})

apiCall.getXSRFCookieValue = () => {
    const cookies = decodeURIComponent(document.cookie).split('; ')
    const xsrfCookieName = `${apiCall.defaults.xsrfCookieName}=`    
    return cookies.find(c => c.startsWith(xsrfCookieName))?.replace(xsrfCookieName, '')
}


// TODO: Serviços com axios para cada tipo de uso axios services 
// apiCall.interceptors.response.use(
//     response => {

//         return { 
//             headers: response.headers, 
//             data: response.data.data, 
//             profile: response.data.profile 
//         }

//     }, 
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
// )

export default apiCall