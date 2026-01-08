<template>
  <div class="root-causes-panel">
    <div class="panel-header">
      <p class="panel-description">
        Analyze root causes from the current filtered data. Select interactions or apply filters to analyze specific complaints.
      </p>
      <button class="analyze-btn" @click="runAnalysis" :disabled="analyzing">
        <span v-if="analyzing">Analyzing...</span>
        <span v-else>Run Analysis</span>
      </button>
    </div>

    <RootCauseCards
      :result="analysisResult"
      :loading="analyzing"
      :filters="filters"
    />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import RootCauseCards from '../RootCauseCards.vue'
import { analyzeRootCauses } from '../../services/api'

const props = defineProps({
  filters: {
    type: Object,
    default: () => ({})
  }
})

const analyzing = ref(false)
const analysisResult = ref(null)

async function runAnalysis() {
  analyzing.value = true
  try {
    const result = await analyzeRootCauses({
      filters: {
        line_of_business: props.filters.lineOfBusiness,
        call_reason: props.filters.callReason,
        product: props.filters.product,
        region: props.filters.region,
        from_date: props.filters.from,
        to_date: props.filters.to,
        complaints_only: true
      }
    })
    analysisResult.value = result
  } catch (error) {
    console.error('Failed to analyze root causes:', error)
    analysisResult.value = null
  } finally {
    analyzing.value = false
  }
}
</script>

<style scoped>
.root-causes-panel {
  padding: 16px;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--td-gray-200);
}

.panel-description {
  font-size: 13px;
  color: var(--td-gray-600);
  margin: 0;
  max-width: 500px;
}

.analyze-btn {
  padding: 8px 16px;
  font-size: 13px;
  font-weight: 500;
  background: var(--td-green);
  border: none;
  border-radius: 6px;
  color: white;
  cursor: pointer;
  transition: background 0.2s;
}

.analyze-btn:hover:not(:disabled) {
  background: var(--td-green-dark, #006B31);
}

.analyze-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>
