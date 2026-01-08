<template>
  <div>
    <BreadcrumbBar :crumbs="[{ label: 'Interactions' }]" />

    <div class="page-header">
      <h1 class="page-title">Interactions</h1>
      <p class="page-subtitle">Browse and analyze individual customer interactions</p>
    </div>

    <GlobalFilterBar
      :show-filters="['lob', 'callReason', 'product', 'region', 'complaintsOnly']"
      @change="handleFilterChange"
    />

    <div class="page-content">
      <!-- KPI Summary -->
      <div class="kpi-grid">
        <div class="kpi-card highlight">
          <div class="kpi-label">Total Interactions</div>
          <div class="kpi-value">{{ metrics.total_interactions?.toLocaleString() }}</div>
        </div>
        <div class="kpi-card warning">
          <div class="kpi-label">Complaints</div>
          <div class="kpi-value">
            {{ metrics.total_complaints?.toLocaleString() }}
            <span class="kpi-unit">({{ metrics.complaint_rate }}%)</span>
          </div>
        </div>
        <div class="kpi-card">
          <div class="kpi-label">Avg Handle Time</div>
          <div class="kpi-value">
            {{ metrics.avg_handling_time_minutes }}
            <span class="kpi-unit">min</span>
          </div>
        </div>
        <div class="kpi-card">
          <div class="kpi-label">First Contact Resolution</div>
          <div class="kpi-value">
            {{ metrics.fcr_rate }}
            <span class="kpi-unit">%</span>
          </div>
        </div>
      </div>

      <!-- Interactions Table with Selection -->
      <InteractionTable
        title="All Interactions"
        :interactions="interactions"
        :total="total"
        :current-page="currentPage"
        :total-pages="totalPages"
        :loading="loading"
        :selectable="true"
        @page-change="handlePageChange"
        @analyze-selected="handleAnalyzeSelected"
      />

      <!-- Root Cause Results -->
      <div v-if="rootCauseResult" class="root-cause-section">
        <div class="section-header">
          <h2>Root Cause Analysis Results</h2>
          <button class="btn btn-secondary btn-sm" @click="clearRootCause">
            Clear Results
          </button>
        </div>
        <RootCauseCards :result="rootCauseResult" />
      </div>
    </div>

    <!-- Loading overlay for analysis -->
    <div v-if="analyzing" class="analysis-overlay">
      <div class="analysis-modal">
        <div class="spinner"></div>
        <p>Analyzing {{ analyzingCount }} interactions...</p>
        <p class="analysis-subtext">Identifying root causes and patterns</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import BreadcrumbBar from '../components/BreadcrumbBar.vue'
import GlobalFilterBar from '../components/GlobalFilterBar.vue'
import InteractionTable from '../components/InteractionTable.vue'
import RootCauseCards from '../components/RootCauseCards.vue'
import { useMainStore } from '../stores/main'
import { getInteractions, getMetrics, analyzeRootCauses } from '../services/api'

const store = useMainStore()

const loading = ref(false)
const analyzing = ref(false)
const analyzingCount = ref(0)
const interactions = ref([])
const total = ref(0)
const currentPage = ref(1)
const totalPages = ref(1)
const rootCauseResult = ref(null)

const metrics = ref({
  total_interactions: 0,
  total_complaints: 0,
  complaint_rate: 0,
  avg_handling_time_minutes: 0,
  fcr_rate: 0
})

async function loadData() {
  loading.value = true
  try {
    const filters = store.globalFilters

    const [interactionsData, metricsData] = await Promise.all([
      getInteractions(filters, currentPage.value, 50),
      getMetrics(filters)
    ])

    interactions.value = interactionsData.data
    total.value = interactionsData.total
    totalPages.value = interactionsData.total_pages

    metrics.value = metricsData
  } catch (error) {
    console.error('Failed to load data:', error)
  } finally {
    loading.value = false
  }
}

function handleFilterChange() {
  currentPage.value = 1
  rootCauseResult.value = null
  loadData()
}

function handlePageChange(page) {
  currentPage.value = page
  loadData()
}

async function handleAnalyzeSelected(selectedIds, selectedInteractions) {
  if (selectedIds.length === 0) return

  analyzing.value = true
  analyzingCount.value = selectedIds.length

  try {
    const result = await analyzeRootCauses({
      interaction_ids: selectedIds
    })
    rootCauseResult.value = result
    store.setLastRootCauseResult(result)

    // Scroll to results
    setTimeout(() => {
      const resultsSection = document.querySelector('.root-cause-section')
      if (resultsSection) {
        resultsSection.scrollIntoView({ behavior: 'smooth' })
      }
    }, 100)
  } catch (error) {
    console.error('Failed to analyze:', error)
  } finally {
    analyzing.value = false
  }
}

function clearRootCause() {
  rootCauseResult.value = null
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.root-cause-section {
  margin-top: 32px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.section-header h2 {
  font-size: 18px;
  font-weight: 600;
  color: var(--td-gray-900);
  margin: 0;
}

/* Analysis overlay */
.analysis-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
}

.analysis-modal {
  background: white;
  border-radius: 12px;
  padding: 32px 48px;
  text-align: center;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
}

.analysis-modal p {
  margin: 16px 0 0;
  font-size: 16px;
  color: var(--td-gray-800);
}

.analysis-subtext {
  font-size: 14px !important;
  color: var(--td-gray-500) !important;
}

.spinner {
  width: 48px;
  height: 48px;
  border: 4px solid var(--td-gray-200);
  border-top-color: var(--td-green);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
</style>
