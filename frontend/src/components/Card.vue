<script setup lang="ts">
import { ref, onMounted } from 'vue';
import axios from 'axios';
import type {MediaItem} from "@/api/interfaces";
import {useRouter} from "vue-router";
import router from "@/router";

const props = defineProps<{
  item: MediaItem;
  mediaType: string;
}>();

const imageUrl = ref('');
const movieApiUrl = 'https://api.themoviedb.org/3/search/movie?api_key=15d2ea6d0dc1d476efbca3eba2b9bbfb&query=';
const animeApiUrl = 'https://kitsu.io/api/edge/anime?filter[text]=';

const navigateToDetails = () => {
  router.push({ name: 'details', params: { item: JSON.stringify(props.item), imageUrl: imageUrl.value } });
};

onMounted(async () => {
    imageUrl.value = "https://eapp.org/wp-content/uploads/2018/05/poster_placeholder.jpg";
    if (props.mediaType == "film") {
      try {
        const response = await axios.get(movieApiUrl + props.item.name);
        if (response.data.results.length === 0) {
          return;
        }
        imageUrl.value = "http://image.tmdb.org/t/p/w500/" + response.data.results[0].poster_path;
      } catch (error) {
        console.error('Error fetching movie image:', error);
      }
    } else {
      try {
        const response = await axios.get(animeApiUrl + props.item.name);
        if (response.data.data && response.data.data.length === 0) {
          return;
        }
        imageUrl.value = response.data.data[0].attributes.posterImage.small;
      } catch (error) {
        console.error('Error fetching anime image:', error);
      }

    }
});
</script>

<template>
  <div class="card" @click="navigateToDetails">
    <img :src="imageUrl" :alt="item.name" class="card-image" />
    <div class="card-title">
      {{ item.name.slice(0, 25) + (item.name.length > 24 ? '...' : '') }}
    </div>
  </div>
</template>

<style scoped>
.card {
  background-color: #313131;
  border-radius: 4px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  cursor: pointer;
}

.card:hover {
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
  transform: translateY(-2px) scale(1.02);
  transition: all 0.3s;
}

.card-image {
  width: 100%;
  height: auto;
  object-fit: cover;
}

.card-title {
  padding: 12px;
  font-size: 16px;
  font-weight: bold;
  text-align: center;
}
</style>