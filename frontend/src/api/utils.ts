import {downloadAnimeFilm, downloadAnimeSeries, downloadFilm, downloadTvSeries} from "@/api/api";
import type {DownloadResponse, Episode, MediaItem} from "@/api/interfaces";

export const handleTVDownload = async (tvShowEpisodes: any[], item: MediaItem) => {
  alertDownload();
  for (const season of tvShowEpisodes) {
    const i = tvShowEpisodes.indexOf(season);
    const res = (await downloadTvSeries(item.id, item.slug, i)).data;
    handleDownloadError(res);
  }
};

export const handleMovieDownload = async (item: MediaItem) => {
  alertDownload();
  const res = (await downloadFilm(item.id, item.slug)).data;
  handleDownloadError(res);
};

export const handleTVAnimeDownload = async (animeEpisodes: Episode[], item: MediaItem) => {
  alertDownload();
  for (const episode of animeEpisodes) {
    const res = (await downloadAnimeSeries(item.id, item.slug, episode.episode_id)).data;
    handleDownloadError(res);
  }
};

export const handleOVADownload = async (item: MediaItem) => {
  alertDownload();
  const res = (await downloadAnimeFilm(item.id, item.slug)).data;
  handleDownloadError(res);
};

const handleDownloadError = (res: DownloadResponse) => {
  if (res.error) {
    throw new Error(`${res.error} - ${res.message}`);
  }
};

export const alertDownload = (message?: any) => {
  if (message) {
    alert(message)
    return;
  }
  alert('Il downlaod è iniziato, il file sarà disponibile tra qualche minuto nella cartella \'Video\' del progetto...')
}