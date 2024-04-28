import axios from 'axios';
import type {MediaItemResponse} from "@/api/interfaces";

const BASE_URL = 'http://127.0.0.1:8000/api'

function get(url: string): Promise<any> {
  return axios.get(`${BASE_URL}${url}`)
    .then(response => response.data)
    .catch(error => {
      throw error;
    });
}

export default function search(query: string, type: string) : Promise<MediaItemResponse> {
    return get(`/search?search_terms=${query}&type=${type}`)
}