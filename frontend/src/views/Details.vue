<script setup lang="ts">
import { useRoute } from 'vue-router'
import type {DownloadResponse, Episode, MediaItem, Season, SeasonResponse} from "@/api/interfaces";
import { onMounted, ref } from "vue";
import {downloadAnimeFilm, downloadFilm, getEpisodesInfo} from "@/api/api";

const route = useRoute()

const item: MediaItem = JSON.parse(<string>route.params.item)
const imageUrl: string = <string>route.params.imageUrl
const animeEpisodes = ref<Episode[]>([])
const tvShowEpisodes = ref<any[]>([])
const loading = ref(false)
const selectingEpisodes = ref(false)

onMounted(async () => {
  if (['MOVIE', 'OVA', 'SPECIAL'].includes(item.type)) {
    return
  } else {
    loading.value = true;
    const response = await getEpisodesInfo(item.id, item.slug, item.type)
    if (response && response.body) {
      loading.value = false;
      const reader = response.body.pipeThrough(new TextDecoderStream()).getReader();
      while (true) {
        const {value, done} = await reader.read();
        if (done) {
          window.scrollTo(0, 0)
          break;
        }
        if (item.type === 'TV_ANIME') {
          const episodesData:Episode = JSON.parse(value.trim());
          animeEpisodes.value.push(episodesData);
        } else {
          const episodesData:SeasonResponse = JSON.parse(value.trim());
          for (const seasonKey in episodesData.episodes) {
            const season = episodesData.episodes[seasonKey];
            const episodes:Episode[] = [];
            for (const episodeKey in season) {
              const episode:Episode = season[episodeKey];
              episodes.push(episode);
            }
            tvShowEpisodes.value.push(episodes);
          }
        }
      }
    }
  }
})

const toggleEpisodeSelection = () => {
  selectingEpisodes.value = !selectingEpisodes.value
}

const downloadItems = async () => {
  try {
    let res: DownloadResponse;
    switch (item.type) {
      case 'MOVIE':
        res = (await downloadFilm(item.id, item.slug)).data;
        break;
      case 'OVA':
      case 'SPECIAL':
        res = (await downloadAnimeFilm(item.id, item.slug)).data;
        break;
      default:
        throw new Error('Tipo di media non supportato');
    }

    console.log(res)

    if (res.error) {
      throw new Error(`${res.error} - ${res.message}`);
    }

    alertDownload();
  } catch (error) {
    alertDownload(error);
  }
};

const alertDownload = (message?: any) => {
  if (message) {
    alert(message)
    return;
  }
  alert('Il downlaod è iniziato, il file sarà disponibile tra qualche minuto nella cartella \'Video\' del progetto...')
}
</script>

<template>
  <div class="details-container">
    <div class="details-card">

      <!--HEADER SECTION-->
      <div class="details-header">
        <img :src="imageUrl" :alt="item.name" class="details-image" />
        <div class="details-title-container">
          <h1 class="details-title">{{ item.name }}</h1>
          <h3>★ {{ item.score }}</h3>
          <div class="details-description">
            <p v-if="['TV_ANIME', 'OVA', 'SPECIAL'].includes(item.type)">{{ item.plot }}</p>
            <p v-else-if="tvShowEpisodes.length > 0">{{ tvShowEpisodes[0][0].plot }}</p>
          </div>
          <h3 v-if="animeEpisodes.length > 0 && !loading">Numero episodi: {{ animeEpisodes[0].episode_total }}</h3>
          <h3 v-if="tvShowEpisodes.length > 0 && !loading">Numero stagioni: {{ tvShowEpisodes.length }}</h3>
          <hr style="opacity: 0.2; margin-top: 10px"/>

          <!--DOWNLOAD SECTION-->
          <div class="download-section">
            <button :disabled="loading || selectingEpisodes" @click="downloadItems">Scarica {{['TV_ANIME', 'TV'].includes(item.type)? 'tutto' : ''}}</button>
            <template v-if="!loading && ['TV_ANIME', 'TV'].includes(item.type)">
              <button @click="toggleEpisodeSelection">{{selectingEpisodes ? 'Disattiva' : 'Attiva'}} selezione episodi</button>
              <button>Download episodi</button>
            </template>
          </div>
        </div>
      </div>

      <!--SERIES SECTION-->
      <div v-if="!loading && ['TV_ANIME', 'TV'].includes(item.type)" :class="item.type == 'TV_ANIME' ? 'episodes-container' : 'season-container'">
          <div v-if="animeEpisodes.length == 0 && tvShowEpisodes.length == 0">
            <p>Non ci sono episodi...</p>
          </div>
          <div v-else-if="item.type == 'TV_ANIME'" v-for="episode in animeEpisodes" :key="episode.id" class="episode-item">
            <div class="episode-title">Episodio {{ episode.number }}</div>
          </div>
          <div v-else-if="item.type == 'TV'" v-for="(season, index) in tvShowEpisodes" class="season-item">
            <div class="season-title">Stagione {{ index + 1 }}</div>
            <div class="episode-container">
              <div v-for="episode in season" :key="episode.id" class="episode-item">
                <div class="episode-title">
                  Episodio {{ episode.number }} -
                  {{episode.name.slice(0, 40) + (episode.name.length > 39 ? '...' : '')}}
                </div>
              </div>
            </div>
          </div>
      </div>

      <!--MOVIES SECTION-->
      <div v-else-if="!loading && ['MOVIE', 'OVA', 'SPECIAL'].includes(item.type)">
        <p>Questo è un {{item.type}} (QUESTO TESTO E' A SCOPO DI TEST)</p>
      </div>

      <!--LOADING SECTION-->
      <div v-else-if="loading">
        <p>Loading...</p>
      </div>
    </div>
  </div>
</template>

<style scoped>
h3 {
  padding-top: 10px;
  padding-bottom: 10px;
  font-weight: bold;
}
.details-container {
  padding-top: 10px;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  width: 200%;
  color: #fff;
}

.details-card {
  width: 100%;
  max-width: 1200px;
  background-color: #232323;
  padding: 2rem;
  border-radius: 0.5rem;
}

.details-header {
  display: flex;
  align-items: flex-start;
  margin-bottom: 2rem;
}

.details-image {
  width: 295px;
  margin-right: 2rem;
  border-radius: 0.5rem;
}

@media (max-width: 1008px) {
  .details-container {
    width: 100%;
  }
  .details-header {
    flex-direction: column;
    align-items: center;
  }

  .details-image {
    max-width: 100%;
    margin-right: 0;
    margin-bottom: 1rem;
  }
}

.details-title-container {
  flex: 1;
}

.details-title {
  font-size: 2rem;
  margin-bottom: 1rem;
}

.details-description {
  line-height: 1.5;
}

.episodes-container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
}

.episode-item {
  background-color: #333;
  padding: 1rem;
  border-radius: 0.5rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  transition: transform 0.3s ease;
  cursor: pointer;
}

.season-item {
  background-color: #2a2a2a;
  padding: 1rem;
  margin-top: 5px;
  margin-bottom: 5px;
  border-radius: 0.5rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.season-item div {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 1rem;
}

.season-title {
  font-size: 1.5rem;
  font-weight: bold;
  padding-bottom: 15px;
}

.episode-item:hover {
  transform: translateY(-5px);
}

.episode-title {
  font-size: 1.2rem;
  font-weight: bold;
}

.download-section {
  margin-top: 1rem;
  flex: fit-content;
  flex-direction: row;
  button {
    margin-right: 5px;
  }
}

@media (max-width: 768px) {
  .episodes-container {
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  }

  .season-item div {
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  }
}
</style>