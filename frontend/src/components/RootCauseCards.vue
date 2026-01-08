<template>
  <div class="root-cause-results">
    <div v-if="loading" class="loading">Analyzing root causes...</div>

    <template v-else-if="result">
      <!-- Executive Summary -->
      <div class="card" style="margin-bottom: 20px; border-left: 4px solid var(--td-green);">
        <div class="card-header">
          <span class="card-title">Executive Summary</span>
        </div>
        <div class="card-body">
          <p style="font-size: 14px; line-height: 1.7;" v-html="formatSummary(result.executive_summary)"></p>
          <p style="margin-top: 12px; font-size: 13px; color: var(--td-gray-600);">
            Analyzed {{ result.total_analyzed }} interactions ({{ result.total_complaints }} complaints)
          </p>
        </div>
      </div>

      <!-- Root Cause Cards -->
      <div v-for="(cause, index) in result.root_causes" :key="cause.root_cause_label" class="root-cause-card">
        <div class="root-cause-header">
          <div>
            <span style="font-size: 13px; color: var(--td-gray-500); margin-right: 8px;">#{{ index + 1 }}</span>
            <span class="root-cause-title">{{ cause.root_cause_label }}</span>
          </div>
          <div style="display: flex; gap: 8px; align-items: center;">
            <span class="badge badge-yellow">Impact: {{ cause.impact_score }}</span>
            <span :class="['concentration-badge', cause.concentration === 'Systemic' ? 'systemic' : 'concentrated']">
              {{ cause.concentration }}
            </span>
            <button
              class="export-btn"
              @click="openExportModal(cause)"
              title="Export data table"
            >
              Export
            </button>
          </div>
        </div>

        <p style="font-size: 13px; color: var(--td-gray-600); margin-bottom: 16px;">
          {{ cause.description }}
        </p>

        <!-- Weekly Trend Chart -->
        <div class="trend-section" v-if="trendData[cause.root_cause_label]">
          <div class="trend-header">
            <span class="trend-title">Weekly Trend</span>
            <span v-if="trendData[cause.root_cause_label].wow_change !== null" :class="['wow-badge', getWowClass(trendData[cause.root_cause_label].wow_change)]">
              {{ trendData[cause.root_cause_label].wow_change > 0 ? '+' : '' }}{{ trendData[cause.root_cause_label].wow_change }}% WoW
            </span>
          </div>
          <apexchart
            type="bar"
            height="120"
            :options="getTrendChartOptions(cause.root_cause_label)"
            :series="getTrendChartSeries(cause.root_cause_label)"
          />
        </div>
        <div v-else-if="loadingTrends[cause.root_cause_label]" class="trend-loading">
          Loading trend...
        </div>

        <div class="root-cause-metrics">
          <div class="root-cause-metric">
            <div class="root-cause-metric-value">{{ cause.frequency }}</div>
            <div class="root-cause-metric-label">Complaints ({{ cause.percentage }}%)</div>
          </div>
          <div class="root-cause-metric">
            <div class="root-cause-metric-value">{{ cause.avg_handling_time_minutes }} min</div>
            <div class="root-cause-metric-label">Avg Handle Time</div>
          </div>
          <div class="root-cause-metric">
            <div class="root-cause-metric-value">{{ cause.fcr_rate }}%</div>
            <div class="root-cause-metric-label">FCR Rate</div>
          </div>
          <div class="root-cause-metric" v-if="cause.top_agent_share">
            <div class="root-cause-metric-value">{{ cause.top_agent_share }}%</div>
            <div class="root-cause-metric-label">Top 3 Agent Share</div>
          </div>
        </div>

        <!-- Top Agents (if concentrated) -->
        <div v-if="cause.concentration === 'Agent-Concentrated' && cause.top_agents?.length" style="margin-bottom: 16px;">
          <div style="font-size: 12px; font-weight: 600; color: var(--td-gray-600); margin-bottom: 8px; text-transform: uppercase;">
            Top Contributing Agents
          </div>
          <div style="display: flex; gap: 12px; flex-wrap: wrap;">
            <div v-for="agent in cause.top_agents" :key="agent.agent_id" class="badge badge-orange">
              {{ agent.agent_name }} ({{ agent.count }})
            </div>
          </div>
        </div>

        <!-- Example Complaints -->
        <div v-if="cause.example_complaints?.length" style="background: var(--td-gray-100); border-radius: 6px; padding: 12px; margin-bottom: 16px;">
          <div style="font-size: 12px; font-weight: 600; color: var(--td-gray-600); margin-bottom: 8px; text-transform: uppercase;">
            Example Complaints
          </div>
          <ul class="bullet-list">
            <li v-for="(example, i) in cause.example_complaints" :key="i" style="font-size: 13px; color: var(--td-gray-700);">
              "{{ example }}"
            </li>
          </ul>
        </div>

        <!-- Suggested Actions -->
        <div style="background: var(--td-green-light); border-radius: 6px; padding: 12px;">
          <div style="font-size: 12px; font-weight: 600; color: var(--td-green); margin-bottom: 8px; text-transform: uppercase;">
            Suggested Actions
          </div>
          <ul style="list-style: none; padding: 0;">
            <li v-for="(action, i) in cause.suggested_actions" :key="i" style="margin-bottom: 8px; font-size: 13px;">
              <span :class="['action-tag', action.type.toLowerCase()]">{{ action.type }}</span>
              {{ action.text }}
            </li>
          </ul>
        </div>
      </div>
    </template>

    <div v-else class="empty-state">
      No analysis results available
    </div>

    <!-- Data Table Modal -->
    <DataTableModal
      :show="showExportModal"
      :title="exportModalTitle"
      :labels="exportModalLabels"
      :rows="exportModalRows"
      row-label="Metric"
      @close="showExportModal = false"
    />
  </div>
</template>

<script setup>
import { ref, reactive, watch } from 'vue'
import DataTableModal from './DataTableModal.vue'
import { getRootCauseTrends } from '../services/api'

const props = defineProps({
  result: {
    type: Object,
    default: null
  },
  loading: {
    type: Boolean,
    default: false
  },
  filters: {
    type: Object,
    default: () => ({})
  }
})

const trendData = reactive({})
const loadingTrends = reactive({})
const showExportModal = ref(false)
const exportModalTitle = ref('')
const exportModalLabels = ref([])
const exportModalRows = ref([])

// Watch for result changes to load trends
watch(() => props.result, async (newResult) => {
  if (newResult?.root_causes) {
    for (const cause of newResult.root_causes) {
      await loadTrendForCause(cause.root_cause_label)
    }
  }
}, { immediate: true })

async function loadTrendForCause(rootCauseLabel) {
  if (trendData[rootCauseLabel] || loadingTrends[rootCauseLabel]) return

  loadingTrends[rootCauseLabel] = true
  try {
    const data = await getRootCauseTrends(rootCauseLabel, props.filters, 8)
    trendData[rootCauseLabel] = data
  } catch (error) {
    console.error(`Failed to load trend for ${rootCauseLabel}:`, error)
  } finally {
    loadingTrends[rootCauseLabel] = false
  }
}

function getTrendChartOptions(rootCauseLabel) {
  const data = trendData[rootCauseLabel]
  if (!data) return {}

  return {
    chart: {
      type: 'bar',
      toolbar: { show: false },
      sparkline: { enabled: false }
    },
    plotOptions: {
      bar: {
        borderRadius: 3,
        columnWidth: '60%'
      }
    },
    colors: ['#00843D'],
    dataLabels: { enabled: false },
    xaxis: {
      categories: data.labels.map(l => l.replace(/^\d{4}-/, '')),
      labels: {
        style: { fontSize: '10px', colors: '#6B7280' }
      }
    },
    yaxis: {
      labels: {
        style: { fontSize: '10px', colors: '#6B7280' }
      }
    },
    grid: {
      borderColor: '#E5E7EB',
      strokeDashArray: 2,
      padding: { left: 0, right: 0 }
    },
    tooltip: {
      y: {
        formatter: (val) => `${val} complaints`
      }
    }
  }
}

function getTrendChartSeries(rootCauseLabel) {
  const data = trendData[rootCauseLabel]
  if (!data) return []

  return [{
    name: 'Complaints',
    data: data.values
  }]
}

function getWowClass(change) {
  if (change === null || change === undefined) return 'neutral'
  // For root causes, lower is better
  return change < 0 ? 'positive' : 'negative'
}

function openExportModal(cause) {
  const data = trendData[cause.root_cause_label]
  if (!data) {
    alert('Trend data not available yet')
    return
  }

  exportModalTitle.value = `${cause.root_cause_label} - Weekly Data`
  exportModalLabels.value = data.labels
  exportModalRows.value = [
    { name: 'Count', values: data.values },
    { name: '% of Total', values: data.percentages }
  ]
  showExportModal.value = true
}

function formatSummary(text) {
  if (!text) return ''
  return text.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
}
</script>

<style scoped>
.export-btn {
  padding: 4px 10px;
  font-size: 11px;
  font-weight: 500;
  background: white;
  border: 1px solid var(--td-gray-300);
  border-radius: 4px;
  color: var(--td-gray-600);
  cursor: pointer;
  transition: all 0.2s;
}

.export-btn:hover {
  background: var(--td-gray-50);
  border-color: var(--td-gray-400);
}

.trend-section {
  background: var(--td-gray-50);
  border-radius: 8px;
  padding: 12px;
  margin-bottom: 16px;
}

.trend-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.trend-title {
  font-size: 12px;
  font-weight: 600;
  color: var(--td-gray-600);
  text-transform: uppercase;
}

.trend-loading {
  background: var(--td-gray-50);
  border-radius: 8px;
  padding: 24px;
  margin-bottom: 16px;
  text-align: center;
  font-size: 12px;
  color: var(--td-gray-500);
}

.wow-badge {
  font-size: 11px;
  font-weight: 600;
  padding: 3px 8px;
  border-radius: 10px;
}

.wow-badge.positive {
  background: #D1FAE5;
  color: #047857;
}

.wow-badge.negative {
  background: #FEE2E2;
  color: #B91C1C;
}

.wow-badge.neutral {
  background: var(--td-gray-200);
  color: var(--td-gray-600);
}
</style>
