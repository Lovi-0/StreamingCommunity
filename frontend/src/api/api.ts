import axios from 'axios'
import type {MediaItemResponse} from '@/api/interfaces'

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

export async function getEpisodesInfo(mediaId: number, mediaSlug: string, mediaType: string): Promise<Response> {
    const url = `${BASE_URL}/search/get_episodes_info?media_id=${mediaId}&media_slug=${mediaSlug}&type_media=${mediaType}`;
    if (mediaType === 'TV_ANIME') {
        return await fetch(url, {
            method: 'GET',
            headers: {
                'Content-Type': 'text/event-stream'
            }
        });
    } else {
        return Promise.resolve(new Response());
    }

}