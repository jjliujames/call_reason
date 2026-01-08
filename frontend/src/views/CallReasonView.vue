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
      <!-- Enhanced KPI Summary - Row 1 -->
      <div class="kpi-grid-enhanced">
        <KpiCard
          label="Call Volume"
          :value="comparison?.current?.total_interactions || metrics.total_interactions || 0"
          format="number"
          :delta="comparison?.deltas?.total_interactions?.absolute"
          :delta-percent="comparison?.deltas?.total_interactions?.percentage"
          :is-positive-good="true"
          variant="highlight"
          :sparkline-data="trendData.volume"
          sparkline-color="#00843D"
        />
        <KpiCard
          label="Complaint Rate"
          :value="comparison?.current?.complaint_rate || metrics.complaint_rate || 0"
          format="percent"
          :delta="comparison?.deltas?.complaint_rate?.absolute"
          :is-positive-good="false"
          :variant="(metrics.complaint_rate || 0) > 25 ? 'danger' : (metrics.complaint_rate || 0) > 18 ? 'warning' : 'default'"
        />
        <KpiCard
          label="FCR Rate"
          :value="comparison?.current?.fcr_rate || metrics.fcr_rate || 0"
          format="percent"
          :delta="comparison?.deltas?.fcr_rate?.absolute"
          :is-positive-good="true"
          :variant="(metrics.fcr_rate || 0) < 60 ? 'danger' : (metrics.fcr_rate || 0) < 75 ? 'warning' : 'success'"
        />
        <KpiCard
          label="Cost per Call"
          :value="comparison?.current?.cost_per_call || 0"
          format="currency"
          :delta="comparison?.deltas?.cost_per_call?.absolute"
          :is-positive-good="false"
        />
      </div>

      <!-- Enhanced KPI Summary - Row 2 -->
      <div class="kpi-grid-enhanced" style="margin-top: 16px;">
        <KpiCard
          label="Avg Handle Time"
          :value="comparison?.current?.avg_handling_time_minutes || metrics.avg_handling_time_minutes || 0"
          format="time"
          :delta="comparison?.deltas?.avg_handling_time_minutes?.absolute"
          :is-positive-good="false"
        />
        <KpiCard
          label="Digital Deflection"
          :value="comparison?.current?.digital_deflection_rate || metrics.deflection_rate || 0"
          format="percent"
          :delta="comparison?.deltas?.digital_deflection_rate?.absolute"
          :is-positive-good="true"
        />
        <KpiCard
          label="Transfer Rate"
          :value="comparison?.current?.transfer_rate || 0"
          format="percent"
          :delta="comparison?.deltas?.transfer_rate?.absolute"
          :is-positive-good="false"
        />
        <KpiCard
          label="Escalation Rate"
          :value="comparison?.current?.escalation_rate || metrics.escalation_rate || 0"
          format="percent"
          :delta="comparison?.deltas?.escalation_rate?.absolute"
          :is-positive-good="false"
        />
      </div>

      <div class="grid-2">
        <!-- Volume Trend Chart -->
        <div class="card">
          <div class="card-header">
            <span class="card-title">Volume Trend</span>
          </div>
          <div class="card-body">
            <apexchart
              v-if="trendData.labels.length"
              type="area"
              height="280"
              :options="volumeChartOptions"
              :series="volumeSeries"
            />
            <div v-else class="empty-state">No trend data</div>
          </div>
        </div>

        <!-- Complaint Trend Chart -->
        <div class="card">
          <div class="card-header">
            <span class="card-title">Complaint Trend</span>
          </div>
          <div class="card-body">
            <apexchart
              v-if="trendData.labels.length"
              type="area"
              height="280"
              :options="complaintChartOptions"
              :series="complaintSeries"
            />
            <div v-else class="empty-state">No trend data</div>
          </div>
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
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import BreadcrumbBar from '../components/BreadcrumbBar.vue'
import GlobalFilterBar from '../components/GlobalFilterBar.vue'
import KpiCard from '../components/KpiCard.vue'
import { useMainStore } from '../stores/main'
import { getMetrics, getTrends, getBreakdown, getMetricsComparison } from '../services/api'

const router = useRouter()
const store = useMainStore()

const loading = ref(false)
const loadingBreakdown = ref(false)

const metrics = ref({})
const comparison = ref(null)
const trendData = ref({ labels: [], volume: [], complaint_volume: [] })
const breakdown = ref([])
const activeTab = ref('line_of_business')

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

// Chart Options
const volumeChartOptions = computed(() => ({
  chart: { toolbar: { show: false }, zoom: { enabled: false } },
  colors: ['#00843D'],
  dataLabels: { enabled: false },
  stroke: { curve: 'smooth', width: 2 },
  fill: { type: 'gradient', gradient: { shadeIntensity: 1, opacityFrom: 0.4, opacityTo: 0.1 } },
  xaxis: {
    categories: trendData.value.labels.map(d => {
      const date = new Date(d)
      return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
    }),
    labels: { rotate: -45 }
  },
  yaxis: { title: { text: 'Interactions' } },
  tooltip: { y: { formatter: val => val + ' interactions' } }
}))

const volumeSeries = computed(() => [{
  name: 'Volume',
  data: trendData.value.volume
}])

const complaintChartOptions = computed(() => ({
  chart: { toolbar: { show: false }, zoom: { enabled: false } },
  colors: ['#DC3545'],
  dataLabels: { enabled: false },
  stroke: { curve: 'smooth', width: 2 },
  fill: { type: 'gradient', gradient: { shadeIntensity: 1, opacityFrom: 0.4, opacityTo: 0.1 } },
  xaxis: {
    categories: trendData.value.labels.map(d => {
      const date = new Date(d)
      return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
    }),
    labels: { rotate: -45 }
  },
  yaxis: { title: { text: 'Complaints' } },
  tooltip: { y: { formatter: val => val + ' complaints' } }
}))

const complaintSeries = computed(() => [{
  name: 'Complaints',
  data: trendData.value.complaint_volume
}])

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
  loadData()
}

onMounted(() => {
  // Determine starting tab based on current filters
  if (store.globalFilters.callReason) {
    activeTab.value = 'product'
  } else if (store.globalFilters.lineOfBusiness) {
    activeTab.value = 'call_reason'
  } else {
    activeTab.value = 'line_of_business'
  }
  loadData()
})
</script>
