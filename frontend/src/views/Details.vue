<script setup lang="ts">
import { useRoute } from 'vue-router'
import type { EpisodeAnime, MediaItem } from "@/api/interfaces";
import { onMounted, ref, onUnmounted } from "vue";
import { getEpisodesInfo } from "@/api/api";

const route = useRoute()

const item: MediaItem = JSON.parse(<string>route.params.item)
const imageUrl: string = <string>route.params.imageUrl
const episodes = ref<EpisodeAnime[]>([])
const loading = ref(false)

onMounted(async () => {
  if (item.type !== 'TV_ANIME' && item.type !== 'TV') {
    return
  }
  loading.value = true
  const response = await getEpisodesInfo(item.id, item.slug, item.type)
  if (response && response.body) {
    loading.value = false;
    const reader = response.body.pipeThrough(new TextDecoderStream()).getReader();
    while (true) {
      const {value, done} = await reader.read();
      if (done) {
        break;
      }
      const episodesData:EpisodeAnime = JSON.parse(value.split("a:")[1].trim());
      episodes.value.push(episodesData);
    }
  }

})
</script>

<template>
  <div class="details-container">
    <div class="details-card">
      <div class="details-header">
        <img :src="imageUrl" :alt="item.name" class="details-image" />
        <div class="details-title-container">
          <h1 class="details-title">{{ item.name }}</h1>
          <h3>★ {{ item.score }}</h3>
          <div class="details-description">
            <p>{{ item.plot }}</p>
          </div>
        </div>
      </div>
      <div class="episodes-container">
        <div v-if="!loading" v-for="episode in episodes" :key="episode.id" class="episode-item">
          <div class="episode-title">{{ episode.number }} - {{ episode.file_name }}</div>
        </div>
        <div v-else>
          <p>Loading...</p>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
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
  max-width: 300px;
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

.details-info {
  display: flex;
  gap: 1rem;
  font-size: 0.9rem;
  color: #999;
}

.details-description {
  padding-top: 10px;
  line-height: 1.5;
}
</style>