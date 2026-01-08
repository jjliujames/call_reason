<template>
  <div>
    <BreadcrumbBar :crumbs="[{ label: 'Root Cause Analysis' }]" />

    <div class="page-header">
      <h1 class="page-title">Root Cause Analysis</h1>
      <p class="page-subtitle">AI-powered analysis of complaint patterns and root causes</p>
    </div>

    <GlobalFilterBar
      :show-filters="['lob', 'callReason', 'product', 'region']"
      @change="handleFilterChange"
    />

    <div class="page-content">
      <!-- Analysis Controls -->
      <div class="card" style="margin-bottom: 24px;">
        <div class="card-body">
          <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
              <h3 style="font-size: 16px; font-weight: 600; margin-bottom: 4px;">Run Analysis</h3>
              <p style="font-size: 13px; color: var(--td-gray-600);">
                Analyze complaints within your current filter selection to identify root causes and patterns.
              </p>
            </div>
            <button
              class="btn btn-primary"
              @click="runAnalysis"
              :disabled="analyzing"
            >
              {{ analyzing ? 'Analyzing...' : 'Run Root Cause Analysis' }}
            </button>
          </div>
        </div>
      </div>

      <!-- Show last result if available -->
      <div v-if="rootCauseResult">
        <RootCauseCards :result="rootCauseResult" :loading="analyzing" />

        <!-- Export / Actions -->
        <div class="card" style="margin-top: 24px;">
          <div class="card-header">
            <span class="card-title">Analysis Actions</span>
          </div>
          <div class="card-body">
            <div style="display: flex; gap: 12px; flex-wrap: wrap;">
              <button class="btn btn-secondary" @click="exportResults">
                Export to CSV
              </button>
              <button class="btn btn-secondary" @click="viewInActions">
                View in Actions & Opportunities
              </button>
              <button class="btn btn-secondary" @click="shareAnalysis">
                Share Analysis
              </button>
            </div>
          </div>
        </div>

        <!-- Concentration Analysis -->
        <div class="card" style="margin-top: 24px;">
          <div class="card-header">
            <span class="card-title">Agent Concentration Analysis</span>
          </div>
          <div class="card-body">
            <div class="grid-2">
              <div>
                <h4 style="font-size: 14px; font-weight: 600; margin-bottom: 12px; color: var(--td-blue);">
                  Systemic Issues
                </h4>
                <p style="font-size: 13px; color: var(--td-gray-600); margin-bottom: 12px;">
                  These root causes are spread across many agents, indicating process or policy issues.
                </p>
                <ul class="bullet-list">
                  <li v-for="cause in systemicCauses" :key="cause.root_cause_label">
                    {{ cause.root_cause_label }} ({{ cause.percentage }}%)
                  </li>
                </ul>
                <div v-if="!systemicCauses.length" class="empty-state" style="padding: 20px;">
                  No systemic issues identified
                </div>
              </div>
              <div>
                <h4 style="font-size: 14px; font-weight: 600; margin-bottom: 12px; color: var(--td-orange);">
                  Agent-Concentrated Issues
                </h4>
                <p style="font-size: 13px; color: var(--td-gray-600); margin-bottom: 12px;">
                  These root causes are concentrated in specific agents, indicating training needs.
                </p>
                <ul class="bullet-list">
                  <li v-for="cause in concentratedCauses" :key="cause.root_cause_label">
                    {{ cause.root_cause_label }} ({{ cause.percentage }}%)
                    <br>
                    <small style="color: var(--td-gray-500);">
                      Top agents: {{ cause.top_agents?.slice(0, 2).map(a => a.agent_name).join(', ') }}
                    </small>
                  </li>
                </ul>
                <div v-if="!concentratedCauses.length" class="empty-state" style="padding: 20px;">
                  No agent-concentrated issues
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Impact Distribution Chart -->
        <div class="card" style="margin-top: 24px;">
          <div class="card-header">
            <span class="card-title">Impact Score Distribution</span>
          </div>
          <div class="card-body">
            <apexchart
              v-if="rootCauseResult.root_causes?.length"
              type="bar"
              height="350"
              :options="impactChartOptions"
              :series="impactSeries"
            />
            <div v-else class="empty-state">No data to display</div>
          </div>
        </div>
      </div>

      <!-- No analysis yet -->
      <div v-else-if="!analyzing" class="placeholder-page">
        <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="var(--td-gray-400)" stroke-width="1.5">
          <path d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"/>
        </svg>
        <h2>No Analysis Results</h2>
        <p>Click "Run Root Cause Analysis" to analyze complaints with current filters.</p>
        <p v-if="store.lastRootCauseResult" style="margin-top: 12px;">
          <button class="btn btn-secondary" @click="loadLastResult">
            Load Previous Analysis
          </button>
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import BreadcrumbBar from '../components/BreadcrumbBar.vue'
import GlobalFilterBar from '../components/GlobalFilterBar.vue'
import RootCauseCards from '../components/RootCauseCards.vue'
import { useMainStore } from '../stores/main'
import { analyzeRootCauses } from '../services/api'

const router = useRouter()
const store = useMainStore()

const analyzing = ref(false)
const rootCauseResult = ref(null)

const systemicCauses = computed(() => {
  if (!rootCauseResult.value?.root_causes) return []
  return rootCauseResult.value.root_causes.filter(c => c.concentration === 'Systemic')
})

const concentratedCauses = computed(() => {
  if (!rootCauseResult.value?.root_causes) return []
  return rootCauseResult.value.root_causes.filter(c => c.concentration === 'Agent-Concentrated')
})

// Chart options
const impactChartOptions = computed(() => ({
  chart: { toolbar: { show: false } },
  colors: ['#00843D'],
  plotOptions: {
    bar: {
      horizontal: true,
      barHeight: '70%',
      distributed: true
    }
  },
  dataLabels: { enabled: true, formatter: val => val.toFixed(0) },
  xaxis: {
    categories: rootCauseResult.value?.root_causes?.map(c => c.root_cause_label) || [],
    title: { text: 'Impact Score' }
  },
  colors: rootCauseResult.value?.root_causes?.map(c =>
    c.concentration === 'Systemic' ? '#2563EB' : '#F97316'
  ) || [],
  legend: { show: false }
}))

const impactSeries = computed(() => [{
  name: 'Impact Score',
  data: rootCauseResult.value?.root_causes?.map(c => c.impact_score) || []
}])

async function runAnalysis() {
  analyzing.value = true
  try {
    const filters = {
      ...store.globalFilters,
      complaints_only: true
    }
    const result = await analyzeRootCauses({ filters })
    rootCauseResult.value = result
    store.setLastRootCauseResult(result)
  } catch (error) {
    console.error('Failed to analyze:', error)
  } finally {
    analyzing.value = false
  }
}

function handleFilterChange() {
  // Optionally auto-run analysis on filter change
  // runAnalysis()
}

function loadLastResult() {
  rootCauseResult.value = store.lastRootCauseResult
}

function exportResults() {
  // Mock export
  alert('Export functionality would download CSV with root cause analysis results.')
}

function viewInActions() {
  router.push('/actions')
}

function shareAnalysis() {
  // Mock share
  alert('Share functionality would generate a shareable link or email the analysis.')
}

onMounted(() => {
  // Load last result if available
  if (store.lastRootCauseResult) {
    rootCauseResult.value = store.lastRootCauseResult
  }
})
</script>
