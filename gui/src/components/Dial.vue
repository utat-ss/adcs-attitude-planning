<script setup lang="ts">
defineProps<{
  min: number,
  max: number,
  value: number,
  title: string,
}>()
</script>

<template>
  <h1>{{ title }}</h1>
</template>

<style scoped>

</style>
