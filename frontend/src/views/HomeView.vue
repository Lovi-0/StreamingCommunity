<script setup lang="ts">
import search from "@/api/api";
import Toggle from "@/components/Toggle.vue";
import { ref } from 'vue'
import type { MediaItem } from "@/api/interfaces";
import Card from "@/components/Card.vue";

const selectedOption = ref('film')
const searchedTitle = ref('')
const searchResults = ref<MediaItem[]>([])

function searchTitle() {
  search(searchedTitle.value, selectedOption.value).then((res) => {
    searchResults.value = res.media
  }).catch((err) => {
    console.log(err)
  })
}
</script>

<template>
  <div class="search-container">
    <div class="search-bar">
      <input
        v-model="searchedTitle"
        @submit="searchTitle"
        class="search-input"
        type="text"
        placeholder="Search for a title..."
      />
      <div class="toggle-button-container">
        <Toggle v-model="selectedOption" class="search-toggle"></Toggle>
        <button @click="searchTitle" class="search-button">Search</button>
      </div>
    </div>
  </div>
  <div class="card-container">
    <div v-for="result in searchResults" :key="result.id" class="card-item">
      <Card :item="result" :media-type="selectedOption" />
    </div>
  </div>
</template>

<style scoped>
.search-container {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  background-color: #313131;
  padding: 16px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  z-index: 1000;
}

.search-bar {
  display: flex;
  align-items: center;
  background-color: #f5f5f5;
  border-radius: 4px;
  padding: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  max-width: 800px;
  margin: 0 auto;
}

.search-input {
  flex-grow: 1;
  border: none;
  background-color: transparent;
  outline: none;
  font-size: 16px;
  padding: 8px;
}

.toggle-button-container {
  display: flex;
  align-items: center;
}

.search-toggle {
  margin: 0 8px;
}

.search-button {
  background-color: #42b883;
  color: white;
  border: none;
  border-radius: 4px;
  padding: 8px 16px;
  font-size: 16px;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.search-button:hover {
  background-color: #3a9f74;
}

.card-container {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  padding: 100px 20px 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.card-item {
  width: 250px;
}

@media (max-width: 768px) {
  .card-container {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 480px) {
  .search-bar {
    flex-wrap: wrap;
  }

  .search-input {
    flex-basis: 100%;
    margin-bottom: 8px;
  }

  .toggle-button-container {
    width: 100%;
    justify-content: space-between;
  }

  .card-container {
    grid-template-columns: 1fr;
  }
}
</style>