<template>
  <SidebarNav />
  <main class="main-content">
    <router-view />
  </main>
</template>

<script setup>
import { onMounted } from 'vue'
import SidebarNav from './components/SidebarNav.vue'
import { useMainStore } from './stores/main'
import { getOptions } from './services/api'

const store = useMainStore()

onMounted(async () => {
  try {
    const options = await getOptions()
    store.setOptions(options)
  } catch (error) {
    console.error('Failed to load options:', error)
  }
})
</script>
