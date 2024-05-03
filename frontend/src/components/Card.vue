<script setup lang="ts">
import { ref, onMounted } from 'vue';
import axios from 'axios';

const props = defineProps<{
  title: string;
  mediaType: string;
}>();

const imageUrl = ref('');
const movieApiUrl = 'https://api.themoviedb.org/3/search/movie?api_key=15d2ea6d0dc1d476efbca3eba2b9bbfb&query=';
const animeApiUrl = 'https://kitsu.io/api/edge/anime?filter[text]=';

onMounted(async () => {
    const searcTerm = props.title.replace(' ', '-');
    if (props.mediaType == "film") {
      try {
        const response = await axios.get(movieApiUrl + props.title);
        if (response.data.results.length === 0) {
          imageUrl.value = "https://eapp.org/wp-content/uploads/2018/05/poster_placeholder.jpg";
          return;
        }
        imageUrl.value = "http://image.tmdb.org/t/p/w500/" + response.data.results[0].poster_path;
      } catch (error) {
        console.error('Error fetching movie image:', error);
      }
    } else {
      try {
        const response = await axios.get(animeApiUrl + props.title);
        // if (response.data.results.length === 0) {
        //   imageUrl.value = "https://eapp.org/wp-content/uploads/2018/05/poster_placeholder.jpg";
        //   return;
        // }
        imageUrl.value = response.data.data[0].attributes.posterImage.small;
      } catch (error) {
        console.error('Error fetching anime image:', error);
      }

    }
});
</script>

<template>
  <div class="card">
    <img :src="imageUrl" :alt="title" class="card-image" />
    <div class="card-title">{{ title }}</div>
  </div>
</template>

<style scoped>
.card {
  background-color: #313131;
  border-radius: 4px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  overflow: hidden;
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