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

      <!-- Interactions Table -->
      <InteractionTable
        title="All Interactions"
        :interactions="interactions"
        :total="total"
        :current-page="currentPage"
        :total-pages="totalPages"
        :loading="loading"
        @page-change="handlePageChange"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import BreadcrumbBar from '../components/BreadcrumbBar.vue'
import GlobalFilterBar from '../components/GlobalFilterBar.vue'
import InteractionTable from '../components/InteractionTable.vue'
import { useMainStore } from '../stores/main'
import { getInteractions, getMetrics } from '../services/api'

const store = useMainStore()

const loading = ref(false)
const interactions = ref([])
const total = ref(0)
const currentPage = ref(1)
const totalPages = ref(1)

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
  loadData()
}

function handlePageChange(page) {
  currentPage.value = page
  loadData()
}

onMounted(() => {
  loadData()
})
</script>
