<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps({
  modelValue: {
    type: String,
    required: true
  }
})

const emit = defineEmits(['update:modelValue'])

const isAnimeSelected = computed(() => props.modelValue === 'anime')

const toggleOption = () => {
  emit('update:modelValue', isAnimeSelected.value ? 'film' : 'anime')
}
</script>

<template>
  <div class="switch-container">
    <span :style="{'color':isAnimeSelected ? '':'green', 'font-weight': isAnimeSelected ? '':'bold'}" class="switch-label-left">Film/Serie TV</span>
    <label class="switch">
      <input type="checkbox" :checked="isAnimeSelected" @change="toggleOption">
      <span class="slider round"></span>
    </label>
    <span :style="{'color':isAnimeSelected ? 'green':'', 'font-weight': isAnimeSelected ? 'bold':''}" class="switch-label-right">Anime</span>
  </div>
</template>

<style scoped>
.switch-container {
  display: flex;
  align-items: center;
}

.switch-label-left,
.switch-label-right {
  font-size: 14px;
  color: #666;
}

.switch {
  position: relative;
  display: inline-block;
  width: 60px;
  height: 34px;
  margin: 0 10px;
}

/* Hide default HTML checkbox */
.switch input {
  opacity: 0;
  width: 0;
  height: 0;
}

/* The slider */
.slider {
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: #42b883;
  -webkit-transition: .4s;
  transition: .4s;
}

.slider:before {
  position: absolute;
  content: "";
  height: 26px;
  width: 26px;
  left: 4px;
  bottom: 4px;
  background-color: white;
  -webkit-transition: .4s;
  transition: .4s;
}

input:checked + .slider {
  background-color: #42b883;
}

input:focus + .slider {
  box-shadow: 0 0 1px #42b883;
}

input:checked + .slider:before {
  -webkit-transform: translateX(26px);
  -ms-transform: translateX(26px);
  transform: translateX(26px);
}

/* Rounded sliders */
.slider.round {
  border-radius: 34px;
}

.slider.round:before {
  border-radius: 50%;
}
</style>