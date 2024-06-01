import {downloadAnimeFilm, downloadAnimeSeries, downloadFilm, downloadTvSeries} from "@/api/api";
import type {DownloadResponse, Episode, MediaItem, Season} from "@/api/interfaces";

export const handleTVDownload = async (tvShowEpisodes: any[], item: MediaItem) => {
  alertDownload();
  for (const season of tvShowEpisodes) {
    const i = tvShowEpisodes.indexOf(season);
    const res = (await downloadTvSeries(item.id, item.slug, i + 1)).data;
    handleDownloadError(res);
  }
};

export const handleTVEpisodesDownload = async (episodes: Episode[], item: MediaItem) => {
    alertDownload();
    for (const episode of episodes) {
        const i = episodes.indexOf(episode);
        const res = (await downloadTvSeries(item.id, item.slug, episode.season_index + 1, i)).data;
        handleDownloadError(res);
    }
}

export const handleMovieDownload = async (item: MediaItem) => {
  alertDownload();
  const res = (await downloadFilm(item.id, item.slug)).data;
  handleDownloadError(res);
};

export const handleTVAnimeDownload = async (episodeCount: number, item: MediaItem) => {
  alertDownload();
  for (let i = 0; i < episodeCount; i++) {
    const res = (await downloadAnimeSeries(item.id, item.slug, i)).data;
    handleDownloadError(res);
  }
};

export const handleTvAnimeEpisodesDownload = async (episodes: Episode[], item: MediaItem) => {
    alertDownload();
    for (const episode of episodes) {
        const res = (await downloadAnimeSeries(item.id, item.slug, episode.episode_id)).data;
        handleDownloadError(res);
    }

}

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