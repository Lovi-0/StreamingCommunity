import axios from "axios";
import type { AxiosResponse } from "axios";
import type { DownloadResponse, MediaItemResponse } from "@/api/interfaces";

const BASE_URL = "http://localhost:8000/api";

const api = axios.create({
  baseURL: BASE_URL,
});

async function get<T>(url: string): Promise<AxiosResponse<T>> {
  return api.get(url);
}

async function post<T>(url: string, data: any): Promise<AxiosResponse<T>> {
  return api.post(url, data);
}

export default function search(
  query: string,
  type: string
): Promise<AxiosResponse<MediaItemResponse>> {
  return get(`/search?search_terms=${query}&type=${type}`);
}

export async function getEpisodesInfo(
  mediaId: number,
  mediaSlug: string,
  mediaType: string
): Promise<Response> {
  const url = `/search/get_episodes_info?media_id=${mediaId}&media_slug=${mediaSlug}&type_media=${mediaType}`;
  return fetch(`${BASE_URL}${url}`, {
    method: "GET",
    headers: {
      "Content-Type": "text/event-stream",
    },
  });
}

export async function getPreview(
  mediaId: number,
  mediaSlug: string,
  mediaType: string
): Promise<AxiosResponse<any>> {
  const url = `/search/get_preview?media_id=${mediaId}&media_slug=${mediaSlug}&type_media=${mediaType}`;
  return get(url);
}

async function downloadMedia(
  mediaId: number,
  mediaSlug: string,
  mediaType: string,
  downloadId?: number,
  tvSeriesEpisodeId?: number
): Promise<AxiosResponse<DownloadResponse>> {
  const url = `/download/`;
  const data = {
    media_id: mediaId,
    media_slug: mediaSlug,
    type_media: mediaType,
    download_id: downloadId,
    tv_series_episode_id: tvSeriesEpisodeId,
  };
  return post(url, data);
}

export const downloadFilm = (mediaId: number, mediaSlug: string) =>
  downloadMedia(mediaId, mediaSlug, "MOVIE");
export const downloadTvSeries = (
  mediaId: number,
  mediaSlug: string,
  downloadId: number,
  tvSeriesEpisodeId?: number
) => downloadMedia(mediaId, mediaSlug, "TV", downloadId, tvSeriesEpisodeId);
export const downloadAnimeFilm = (mediaId: number, mediaSlug: string) =>
  downloadMedia(mediaId, mediaSlug, "OVA");
export const downloadAnimeSeries = (
  mediaId: number,
  mediaSlug: string,
  downloadId: number
) => downloadMedia(mediaId, mediaSlug, "TV_ANIME", downloadId);
