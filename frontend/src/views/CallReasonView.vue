<template>
  <div>
    <BreadcrumbBar :crumbs="breadcrumbs" />

    <div class="page-header">
      <h1 class="page-title">Call Reason Analysis</h1>
      <p class="page-subtitle">Analyze call volume and metrics by taxonomy hierarchy</p>
    </div>

    <GlobalFilterBar
      :show-filters="['lob', 'callReason', 'product', 'region', 'complaintsOnly']"
      @change="handleFilterChange"
    />

    <div class="page-content">
      <!-- Enhanced KPI Summary - Single Row (6 KPIs) -->
      <div class="kpi-grid-6">
        <KpiCard
          label="Call Volume"
          :value="comparison?.current?.total_interactions || metrics.total_interactions || 0"
          format="number"
          :delta="comparison?.deltas?.total_interactions?.absolute"
          :delta-percent="comparison?.deltas?.total_interactions?.percentage"
          :is-positive-good="true"
          :variant="selectedMetric === 'volume' ? 'highlight' : 'default'"
          :clickable="true"
          @click="selectMetric('volume')"
        />
        <KpiCard
          label="Complaint Rate"
          :value="comparison?.current?.complaint_rate || metrics.complaint_rate || 0"
          format="percent"
          :delta="comparison?.deltas?.complaint_rate?.absolute"
          :is-positive-good="false"
          :variant="selectedMetric === 'complaint_rate' ? 'highlight' : ((metrics.complaint_rate || 0) > 25 ? 'danger' : (metrics.complaint_rate || 0) > 18 ? 'warning' : 'default')"
          :clickable="true"
          @click="selectMetric('complaint_rate')"
        />
        <KpiCard
          label="FCR Rate"
          :value="comparison?.current?.fcr_rate || metrics.fcr_rate || 0"
          format="percent"
          :delta="comparison?.deltas?.fcr_rate?.absolute"
          :is-positive-good="true"
          :variant="selectedMetric === 'fcr_rate' ? 'highlight' : ((metrics.fcr_rate || 0) < 60 ? 'danger' : (metrics.fcr_rate || 0) < 75 ? 'warning' : 'success')"
          :clickable="true"
          @click="selectMetric('fcr_rate')"
        />
        <KpiCard
          label="Avg Handle Time"
          :value="comparison?.current?.avg_handling_time_minutes || metrics.avg_handling_time_minutes || 0"
          format="time"
          :delta="comparison?.deltas?.avg_handling_time_minutes?.absolute"
          :is-positive-good="false"
          :variant="selectedMetric === 'avg_handling_time' ? 'highlight' : 'default'"
          :clickable="true"
          @click="selectMetric('avg_handling_time')"
        />
        <KpiCard
          label="Transfer Rate"
          :value="comparison?.current?.transfer_rate || 0"
          format="percent"
          :delta="comparison?.deltas?.transfer_rate?.absolute"
          :is-positive-good="false"
          :variant="selectedMetric === 'transfer_rate' ? 'highlight' : 'default'"
          :clickable="true"
          @click="selectMetric('transfer_rate')"
        />
        <KpiCard
          label="Escalation Rate"
          :value="comparison?.current?.escalation_rate || metrics.escalation_rate || 0"
          format="percent"
          :delta="comparison?.deltas?.escalation_rate?.absolute"
          :is-positive-good="false"
          :variant="selectedMetric === 'escalation_rate' ? 'highlight' : 'default'"
          :clickable="true"
          @click="selectMetric('escalation_rate')"
        />
      </div>

      <!-- Weekly Trend Chart (replaces Volume/Complaint trends when metric selected) -->
      <div class="card">
        <div class="card-header">
          <span class="card-title">{{ selectedMetricLabel }} - Weekly Trend</span>
          <div v-if="selectedMetricTrend" class="trend-summary">
            <span :class="['wow-badge', getWowClass(selectedMetricTrend.wow_change)]">
              {{ selectedMetricTrend.wow_change > 0 ? '+' : '' }}{{ selectedMetricTrend.wow_change }}% WoW
            </span>
          </div>
        </div>
        <div class="card-body">
          <div v-if="loadingTrend" class="loading">Loading weekly trends...</div>
          <apexchart
            v-else-if="selectedMetricTrend"
            type="bar"
            height="300"
            :options="weeklyChartOptions"
            :series="weeklyChartSeries"
          />
          <div v-else class="empty-state">Select a metric above to view weekly trends</div>
        </div>
      </div>

      <!-- Drill-Down Tabs -->
      <div class="card" style="margin-top: 24px;">
        <div class="tabs">
          <button
            class="tab"
            :class="{ active: activeTab === 'line_of_business' }"
            @click="changeTab('line_of_business')"
          >
            By Line of Business
          </button>
          <button
            class="tab"
            :class="{ active: activeTab === 'call_reason' }"
            @click="changeTab('call_reason')"
          >
            By Call Reason
          </button>
          <button
            class="tab"
            :class="{ active: activeTab === 'product' }"
            @click="changeTab('product')"
          >
            By Product
          </button>
        </div>

        <div class="card-body">
          <div v-if="loadingBreakdown" class="loading">Loading breakdown...</div>

          <table v-else-if="breakdown.length" class="data-table">
            <thead>
              <tr>
                <th>{{ getColumnLabel() }}</th>
                <th>Interactions</th>
                <th>Complaints</th>
                <th>Complaint Rate</th>
                <th>Avg Handle Time</th>
                <th>FCR Rate</th>
                <th>Total Cost</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="item in breakdown"
                :key="item.label"
                @click="handleDrillDown(item)"
              >
                <td>
                  <span class="link">{{ item.label }}</span>
                </td>
                <td>{{ item.count.toLocaleString() }}</td>
                <td>{{ item.complaint_count.toLocaleString() }}</td>
                <td>
                  <span :class="['badge', item.complaint_rate > 25 ? 'badge-red' : item.complaint_rate > 15 ? 'badge-orange' : 'badge-green']">
                    {{ item.complaint_rate }}%
                  </span>
                </td>
                <td>{{ item.avg_handling_time_minutes }} min</td>
                <td>
                  <span :class="['badge', item.fcr_rate < 60 ? 'badge-red' : item.fcr_rate < 75 ? 'badge-orange' : 'badge-green']">
                    {{ item.fcr_rate }}%
                  </span>
                </td>
                <td>${{ item.total_cost.toLocaleString() }}</td>
              </tr>
            </tbody>
          </table>

          <div v-else class="empty-state">No breakdown data available</div>
        </div>
      </div>

      <!-- Bar Chart -->
      <div class="card" style="margin-top: 24px;">
        <div class="card-header">
          <span class="card-title">Volume by {{ getColumnLabel() }}</span>
        </div>
        <div class="card-body">
          <apexchart
            v-if="breakdown.length"
            type="bar"
            height="350"
            :options="barChartOptions"
            :series="barSeries"
          />
          <div v-else class="empty-state">No data</div>
        </div>
      </div>

      <!-- Analysis Section -->
      <AnalysisSection
        :filters="store.globalFilters"
        :tabs="['trends', 'segments', 'products', 'root_causes']"
        @filter-change="handleAnalysisFilterChange"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import BreadcrumbBar from '../components/BreadcrumbBar.vue'
import GlobalFilterBar from '../components/GlobalFilterBar.vue'
import KpiCard from '../components/KpiCard.vue'
import AnalysisSection from '../components/AnalysisSection.vue'
import { useMainStore } from '../stores/main'
import { getMetrics, getTrends, getBreakdown, getMetricsComparison, getWeeklyTrends } from '../services/api'

const router = useRouter()
const store = useMainStore()

const loading = ref(false)
const loadingBreakdown = ref(false)
const loadingTrend = ref(false)

const metrics = ref({})
const comparison = ref(null)
const trendData = ref({ labels: [], volume: [], complaint_volume: [] })
const breakdown = ref([])
const activeTab = ref('line_of_business')
const selectedMetric = ref('volume')
const weeklyTrendData = ref(null)

const metricLabels = {
  volume: 'Call Volume',
  complaint_rate: 'Complaint Rate',
  fcr_rate: 'FCR Rate',
  avg_handling_time: 'Avg Handle Time',
  transfer_rate: 'Transfer Rate',
  escalation_rate: 'Escalation Rate'
}

const selectedMetricLabel = computed(() => metricLabels[selectedMetric.value] || 'Metric')
const selectedMetricTrend = computed(() => weeklyTrendData.value)

const breadcrumbs = computed(() => {
  const crumbs = [{ label: 'Call Reason Analysis' }]
  if (store.globalFilters.lineOfBusiness) {
    crumbs.push({ label: store.globalFilters.lineOfBusiness })
  }
  if (store.globalFilters.callReason) {
    crumbs.push({ label: store.globalFilters.callReason })
  }
  if (store.globalFilters.product) {
    crumbs.push({ label: store.globalFilters.product })
  }
  return crumbs
})

// Weekly Chart Options
const weeklyChartOptions = computed(() => ({
  chart: {
    type: 'bar',
    toolbar: { show: false },
    animations: { enabled: true }
  },
  plotOptions: {
    bar: {
      borderRadius: 6,
      columnWidth: '60%'
    }
  },
  colors: ['#00843D'],
  dataLabels: { enabled: false },
  xaxis: {
    categories: weeklyTrendData.value?.labels?.map(l => l.replace(/^\d{4}-/, '')) || [],
    labels: {
      style: { fontSize: '11px', colors: '#6B7280' }
    }
  },
  yaxis: {
    labels: {
      style: { fontSize: '11px', colors: '#6B7280' },
      formatter: (val) => {
        if (selectedMetric.value === 'volume') {
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
    }
  },
  grid: {
    borderColor: '#E5E7EB',
    strokeDashArray: 3
  },
  tooltip: {
    y: {
      formatter: (val) => formatMetricValue(val, selectedMetric.value)
    }
  }
}))

const weeklyChartSeries = computed(() => [{
  name: selectedMetricLabel.value,
  data: weeklyTrendData.value?.values || []
}])

function formatMetricValue(val, metric) {
  if (val === null || val === undefined) return '—'
  if (metric === 'volume') return val.toLocaleString()
  if (['complaint_rate', 'fcr_rate', 'transfer_rate', 'escalation_rate'].includes(metric)) return `${val}%`
  if (metric === 'avg_handling_time') return `${val} min`
  return val.toLocaleString()
}

function getWowClass(change) {
  if (change === null || change === undefined) return 'neutral'
  // For most metrics, lower is better (complaints, escalation, etc.)
  // Only volume and fcr_rate - higher is better
  const positiveIsGood = ['volume', 'fcr_rate'].includes(selectedMetric.value)
  const isUp = change > 0
  const isGood = positiveIsGood ? isUp : !isUp
  return isGood ? 'positive' : 'negative'
}

const barChartOptions = computed(() => ({
  chart: { toolbar: { show: false } },
  colors: ['#00843D', '#DC3545'],
  plotOptions: { bar: { horizontal: true, barHeight: '70%' } },
  dataLabels: { enabled: false },
  xaxis: { categories: breakdown.value.map(b => b.label.length > 25 ? b.label.slice(0, 25) + '...' : b.label) },
  legend: { position: 'top' }
}))

const barSeries = computed(() => [
  { name: 'Total Interactions', data: breakdown.value.map(b => b.count) },
  { name: 'Complaints', data: breakdown.value.map(b => b.complaint_count) }
])

function getColumnLabel() {
  switch (activeTab.value) {
    case 'line_of_business': return 'Line of Business'
    case 'call_reason': return 'Call Reason'
    case 'product': return 'Product'
    default: return 'Category'
  }
}

async function loadData() {
  loading.value = true
  try {
    const filters = store.globalFilters

    // Calculate date ranges for comparison
    const toDate = filters.to || new Date().toISOString().split('T')[0]
    const fromDate = filters.from || new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0]

    const [metricsData, trendsData, comparisonData] = await Promise.all([
      getMetrics(filters),
      getTrends(filters, 'daily'),
      getMetricsComparison(fromDate, toDate, filters).catch(() => null)
    ])

    metrics.value = metricsData
    trendData.value = trendsData
    comparison.value = comparisonData

    await loadBreakdown()
  } catch (error) {
    console.error('Failed to load data:', error)
  } finally {
    loading.value = false
  }
}

async function loadBreakdown() {
  loadingBreakdown.value = true
  try {
    const result = await getBreakdown(store.globalFilters, activeTab.value)
    breakdown.value = result.data
  } catch (error) {
    console.error('Failed to load breakdown:', error)
    breakdown.value = []
  } finally {
    loadingBreakdown.value = false
  }
}

function changeTab(tab) {
  activeTab.value = tab
  loadBreakdown()
}

function handleDrillDown(item) {
  const newFilters = { ...store.globalFilters }

  if (activeTab.value === 'line_of_business') {
    newFilters.lineOfBusiness = item.label
    activeTab.value = 'call_reason'
  } else if (activeTab.value === 'call_reason') {
    newFilters.callReason = item.label
    activeTab.value = 'product'
  } else if (activeTab.value === 'product') {
    newFilters.product = item.label
    router.push('/interactions')
    return
  }

  store.setGlobalFilters(newFilters)
  loadData()
}

function handleFilterChange() {
  // Clear weekly trend data when filters change
  weeklyTrendData.value = null
  loadData()
  // Reload the selected metric trend
  if (selectedMetric.value) {
    loadWeeklyTrend(selectedMetric.value)
  }
}

async function selectMetric(metricKey) {
  selectedMetric.value = metricKey
  await loadWeeklyTrend(metricKey)
}

async function loadWeeklyTrend(metricKey) {
  loadingTrend.value = true
  try {
    const filters = store.globalFilters
    const data = await getWeeklyTrends(metricKey, filters, 8)
    weeklyTrendData.value = data
  } catch (error) {
    console.error('Failed to load weekly trends:', error)
    weeklyTrendData.value = null
  } finally {
    loadingTrend.value = false
  }
}

function handleAnalysisFilterChange(newFilters) {
  // Update global filters when Analysis Section selection changes
  store.setGlobalFilters(newFilters)
  loadData()
}

onMounted(async () => {
  // Determine starting tab based on current filters
  if (store.globalFilters.callReason) {
    activeTab.value = 'product'
  } else if (store.globalFilters.lineOfBusiness) {
    activeTab.value = 'call_reason'
  } else {
    activeTab.value = 'line_of_business'
  }
  await loadData()
  // Load initial weekly trend for default metric
  loadWeeklyTrend(selectedMetric.value)
})
</script>
