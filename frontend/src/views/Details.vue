<template>
  <div class="details-container">
    <div class="details-card">
      <div class="details-header">
        <img :src="imageUrl" :alt="item.name" class="details-image" />
        <div class="details-title-container">
          <h1 class="details-title">{{ item.name }}</h1>
          <div class="details-description">
            <p>{{ item.plot }}</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRoute } from 'vue-router'
import type { MediaItem } from "@/api/interfaces";

const route = useRoute()

const item: MediaItem = JSON.parse(<string>route.params.item)
const imageUrl: string = <string>route.params.imageUrl
</script>

<style scoped>
.details-container {
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
  line-height: 1.5;
}
</style>