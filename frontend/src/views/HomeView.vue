<script setup lang="ts">
import search from "@/api/api";
import Toggle from "@/components/Toggle.vue";
import { ref, watch } from 'vue'
import type { MediaItem } from "@/api/interfaces";
import Card from "@/components/Card.vue";
import { onBeforeRouteLeave } from 'vue-router'

const selectedOption = ref('film')
const searchedTitle = ref('')
const searchResults = ref<MediaItem[]>([])

const storeSearchResults = () => {
  localStorage.setItem('searchResults', JSON.stringify(searchResults.value))
  localStorage.setItem('selectedOption', selectedOption.value)
}

const retrieveSearchResults = () => {
  const storedResults = localStorage.getItem('searchResults')
  try {
    if (!storedResults) return
    searchResults.value = JSON.parse(storedResults)
    selectedOption.value = localStorage.getItem('selectedOption') || 'film'
  } catch (e) {
  }
}

watch(searchResults, storeSearchResults, { deep: true })

retrieveSearchResults()

function searchTitle() {
  search(searchedTitle.value, selectedOption.value).then((res) => {
    searchResults.value = res.data.media
  }).catch((err) => {
    console.log(err)
  })
  storeSearchResults()
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
        placeholder="Cerca un titolo..."
      />
      <div class="toggle-button-container">
        <Toggle style="margin-right: 30px" v-model="selectedOption" class="search-toggle"></Toggle>
        <button @click="searchTitle">Cerca</button>
      </div>
    </div>
  </div>
  <div v-if="searchResults && searchResults.length > 0" class="card-container">
    <div v-for="result in searchResults" :key="result.id" class="card-item">
      <Card :item="result" :media-type="selectedOption" />
    </div>
  </div>
  <div v-else>
    <p style="text-align: center; margin-top: 100px;">Nessun risultato trovato</p>
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

.card-container {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  padding: 100px 8% 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.card-item {
  width: 250px;
}

@media (max-width: 768px) {
  .card-container {
    grid-template-columns: repeat(2, 1fr);
    padding: 120px 12% 20px;
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