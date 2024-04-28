<script setup lang="ts">

import search from "@/api/api";
import Toggle from "@/components/Toggle.vue";

function testSearch() {
  search('naruto', 'anime').then((res) => {
    console.log(res.media[0])
  }).catch((err) => {
    console.log(err)
  })
}
</script>

<template>
  <div>
    <button @click="testSearch">test search</button>
    <toggle></toggle>
  </div>
</template>