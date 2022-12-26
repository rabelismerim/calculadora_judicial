import router from '../router'

export default {

    isStringVoid: (value) => (
        (value == null) || (
            ((typeof value === 'string') || (value instanceof String)) && !value.trim()
        )
    ),

    apiResponseHandler: (dispatch, resolve, data, showSnackOnError=true) => {

        if (!Object.prototype.hasOwnProperty.call(data, 'error')) {
            resolve(data.data)
        } else {
            resolve(false)
        
            const [homeRedirect, snackDelay, snackText] = (
                (data.error === 'SERVER_UNAUTHORIZED')
                && [true, 500, 'Sem acesso.']
                || [false, 0, 'Ocorreu um erro.']
            )
            if (showSnackOnError) {
                dispatch('setSnack', {
                    delay: snackDelay,
                    type: 'error',
                    text: snackText,
                    showContact: true
                })
            }
            if (homeRedirect) {
                router.push({ name: 'Home' })
            }
        }
      
    }        
}