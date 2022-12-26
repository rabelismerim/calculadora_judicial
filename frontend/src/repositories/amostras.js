import axios from '@/plugins/axios'

const endpoint = '/amostras/';

export default {
    find(id) {
        return axios.get(endpoint+id);
    },
    list() {
        return axios.get(endpoint);
    },
    update(id, infos){
        return axios.put(endpoint+id,JSON.stringify(infos),{headers: {"Content-Type": "application/json"}});
    },
    delete(id){
        return axios.delete(endpoint+id);
    },
}