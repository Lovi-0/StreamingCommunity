import axios from 'axios'
import type {MediaItemResponse} from '@/api/interfaces'

const BASE_URL = 'http://localhost:8000/api'

function get(url: string): Promise<any> {
  return axios.get(`${BASE_URL}${url}`)
    .then(response => response.data)
    .catch(error => {
      throw error;
    });
}

function post(url: string, data: any): Promise<any> {
  return axios.post(`${BASE_URL}${url}`, data)
    .then(response => response.data)
    .catch(error => {
      throw error;
    });
}

export default function search(query: string, type: string) : Promise<MediaItemResponse> {
    return get(`/search?search_terms=${query}&type=${type}`)
}

export async function getEpisodesInfo(mediaId: number, mediaSlug: string, mediaType: string): Promise<Response> {
    const url = `${BASE_URL}/search/get_episodes_info?media_id=${mediaId}&media_slug=${mediaSlug}&type_media=${mediaType}`;
    return await fetch(url, {
        method: 'GET',
        headers: {
            'Content-Type': 'text/event-stream'
        }
    });
}

export async function downloadFilm(mediaId: number, mediaSlug: string, mediaType: string): Promise<Response> {
    const url = `/download/`;
    const data = {
        media_id: mediaId,
        media_slug: mediaSlug,
        type_media: mediaType
    };
    return post(url, data);
}