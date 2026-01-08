<template>
  <div class="trends-panel">
    <div class="panel-header">
      <div class="metric-selector">
        <label>Metric:</label>
        <select v-model="selectedMetric" @change="loadTrend">
          <option value="volume">Call Volume</option>
          <option value="complaint_volume_rate">Complaint Volume (Rate)</option>
          <option value="complaint_rate">Complaint Rate</option>
          <option value="fcr_rate">FCR Rate</option>
          <option value="avg_handling_time">Avg Handle Time</option>
          <option value="transfer_rate">Transfer Rate</option>
          <option value="escalation_rate">Escalation Rate</option>
        </select>
      </div>
      <div class="panel-actions">
        <button class="export-btn" @click="openExport" :disabled="!trendData">Export</button>
      </div>
    </div>

    <div v-if="loading" class="loading">Loading weekly trends...</div>

    <div v-else-if="trendData" class="trend-chart-container">
      <div class="trend-summary">
        <span class="current-value">{{ formatValue(trendData.current_value) }}</span>
        <span v-if="trendData.wow_change !== null" :class="['wow-badge', getWowClass(trendData.wow_change)]">
          {{ trendData.wow_change > 0 ? '+' : '' }}{{ trendData.wow_change }}% WoW
        </span>
      </div>

      <apexchart
        type="bar"
        height="300"
        :options="chartOptions"
        :series="chartSeries"
      />
    </div>

    <div v-else class="empty-state">
      Select a metric to view weekly trends
    </div>

    <DataTableModal
      :show="showExportModal"
      :title="`${metricLabels[selectedMetric]} - Weekly Data`"
      :labels="trendData?.labels || []"
      :rows="exportRows"
      row-label="Metric"
      @close="showExportModal = false"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import DataTableModal from '../DataTableModal.vue'
import { getWeeklyTrends } from '../../services/api'

const props = defineProps({
  filters: {
    type: Object,
    default: () => ({})
  }
})

const selectedMetric = ref('volume')
const trendData = ref(null)
const loading = ref(false)
const showExportModal = ref(false)

const metricLabels = {
  volume: 'Call Volume',
  complaint_volume_rate: 'Complaint Volume (Rate)',
  complaint_rate: 'Complaint Rate',
  fcr_rate: 'FCR Rate',
  avg_handling_time: 'Avg Handle Time',
  transfer_rate: 'Transfer Rate',
  escalation_rate: 'Escalation Rate'
}

const chartOptions = computed(() => ({
  chart: {
    type: 'bar',
    toolbar: { show: false }
  },
  plotOptions: {
    bar: {
      borderRadius: 6,
      columnWidth: '60%',
      dataLabels: {
        position: 'top'
      }
    }
  },
  colors: ['#00843D'],
  dataLabels: {
    enabled: true,
    formatter: (val, opts) => {
      // For complaint_volume_rate, show the rate % as the label
      if (selectedMetric.value === 'complaint_volume_rate' && trendData.value?.rates) {
        const rate = trendData.value.rates[opts.dataPointIndex]
        return rate !== undefined ? `${rate}%` : ''
      }
      // For other metrics, show the formatted value
      return formatValue(val)
    },
    style: {
      fontSize: '10px',
      fontWeight: 600,
      colors: ['#374151']
    },
    offsetY: -20
  },
  xaxis: {
    categories: trendData.value?.labels?.map(l => l.replace(/^\d{4}-/, '')) || [],
    labels: {
      style: { fontSize: '11px', colors: '#6B7280' }
    }
  },
  yaxis: {
    labels: {
      style: { fontSize: '11px', colors: '#6B7280' },
      formatter: (val) => formatYAxisValue(val)
    }
  },
  grid: {
    borderColor: '#E5E7EB',
    strokeDashArray: 3
  },
  tooltip: {
    y: {
      formatter: (val, opts) => {
        // For complaint_volume_rate, show both volume and rate in tooltip
        if (selectedMetric.value === 'complaint_volume_rate' && trendData.value?.rates) {
          const rate = trendData.value.rates[opts.dataPointIndex]
          return `${val.toLocaleString()} complaints (${rate}% rate)`
        }
        return formatValue(val)
      }
    }
  }
}))

const chartSeries = computed(() => [{
  name: metricLabels[selectedMetric.value],
  data: trendData.value?.values || []
}])

const exportRows = computed(() => {
  if (!trendData.value) return []
  return [
    { name: metricLabels[selectedMetric.value], values: trendData.value.values }
  ]
})

function formatValue(val) {
  if (val === null || val === undefined) return '—'
  if (selectedMetric.value === 'volume' || selectedMetric.value === 'complaint_volume_rate') {
    return val >= 1000 ? `${(val / 1000).toFixed(1)}k` : val.toLocaleString()
  }
  if (['complaint_rate', 'fcr_rate', 'transfer_rate', 'escalation_rate'].includes(selectedMetric.value)) {
    return `${val}%`
  }
  if (selectedMetric.value === 'avg_handling_time') {
    return `${val} min`
  }
  return val.toLocaleString()
}

function formatYAxisValue(val) {
  if (val === null || val === undefined) return '—'
  if (selectedMetric.value === 'volume' || selectedMetric.value === 'complaint_volume_rate') {
    return val >= 1000 ? `${(val / 1000).toFixed(1)}k` : val
  }
  if (['complaint_rate', 'fcr_rate', 'transfer_rate', 'escalation_rate'].includes(selectedMetric.value)) {
    return `${val}%`
  }
  if (selectedMetric.value === 'avg_handling_time') {
    return `${val}m`
  }
  return val
}

function getWowClass(change) {
  if (change === null || change === undefined) return 'neutral'
  // For volume and fcr_rate, higher is better
  // For complaint_volume_rate, lower is better (fewer complaints)
  const positiveIsGood = ['volume', 'fcr_rate'].includes(selectedMetric.value)
  const isUp = change > 0
  return (positiveIsGood ? isUp : !isUp) ? 'positive' : 'negative'
}

async function loadTrend() {
  loading.value = true
  try {
    const data = await getWeeklyTrends(selectedMetric.value, props.filters, 8)
    trendData.value = data
  } catch (error) {
    console.error('Failed to load trends:', error)
    trendData.value = null
  } finally {
    loading.value = false
  }
}

function openExport() {
  showExportModal.value = true
}

watch(() => props.filters, () => {
  loadTrend()
}, { deep: true })

onMounted(() => {
  loadTrend()
})
</script>

<style scoped>
.trends-panel {
  padding: 16px;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.metric-selector {
  display: flex;
  align-items: center;
  gap: 8px;
}

.metric-selector label {
  font-size: 13px;
  color: var(--td-gray-600);
}

.metric-selector select {
  padding: 6px 10px;
  border: 1px solid var(--td-gray-300);
  border-radius: 6px;
  font-size: 13px;
  background: white;
}

.export-btn {
  padding: 6px 12px;
  font-size: 12px;
  font-weight: 500;
  background: white;
  border: 1px solid var(--td-gray-300);
  border-radius: 6px;
  cursor: pointer;
}

.export-btn:hover:not(:disabled) {
  background: var(--td-gray-50);
}

.export-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.trend-chart-container {
  background: var(--td-gray-50);
  border-radius: 8px;
  padding: 16px;
}

.trend-summary {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.current-value {
  font-size: 24px;
  font-weight: 700;
  color: var(--td-gray-900);
}

.wow-badge {
  font-size: 12px;
  font-weight: 600;
  padding: 4px 10px;
  border-radius: 12px;
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

.loading, .empty-state {
  padding: 40px;
  text-align: center;
  color: var(--td-gray-500);
  font-size: 13px;
}
</style>
