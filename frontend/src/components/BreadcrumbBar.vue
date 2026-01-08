<template>
  <div class="breadcrumb-bar">
    <nav class="breadcrumb">
      <router-link to="/" class="breadcrumb-item">Home</router-link>
      <template v-for="(crumb, index) in crumbs" :key="index">
        <span class="breadcrumb-separator">›</span>
        <router-link
          v-if="crumb.to && index < crumbs.length - 1"
          :to="crumb.to"
          class="breadcrumb-item"
          @click="handleCrumbClick(crumb)"
        >
          {{ crumb.label }}
        </router-link>
        <span v-else class="breadcrumb-item current">{{ crumb.label }}</span>
      </template>
    </nav>
  </div>
</template>

<script setup>
import { useMainStore } from '../stores/main'

defineProps({
  crumbs: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['navigate'])
const store = useMainStore()

function handleCrumbClick(crumb) {
  if (crumb.filters) {
    store.setGlobalFilters(crumb.filters)
  }
  emit('navigate', crumb)
}
</script>
