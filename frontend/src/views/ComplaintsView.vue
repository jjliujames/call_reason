<template>
  <div>
    <BreadcrumbBar :crumbs="[{ label: 'Complaints Analysis' }]" />

    <div class="page-header">
      <h1 class="page-title">Complaints Analysis</h1>
      <p class="page-subtitle">Deep dive into customer complaints and identify improvement areas</p>
    </div>

    <GlobalFilterBar
      :show-filters="['lob', 'callReason', 'product', 'region']"
      @change="handleFilterChange"
    />

    <div class="page-content">
      <!-- Enhanced KPI Summary - Row 1 -->
      <div class="kpi-grid-enhanced">
        <KpiCard
          label="Total Complaints"
          :value="comparison?.current?.total_complaints || metrics.total_complaints || 0"
          format="number"
          :delta="comparison?.deltas?.total_complaints?.absolute"
          :is-positive-good="false"
          variant="danger"
          :sparkline-data="trendData.complaint_volume"
          sparkline-color="#DC3545"
        />
        <KpiCard
          label="Complaint Rate"
          :value="comparison?.current?.complaint_rate || metrics.complaint_rate || 0"
          format="percent"
          :delta="comparison?.deltas?.complaint_rate?.absolute"
          :is-positive-good="false"
          variant="warning"
        />
        <KpiCard
          label="High Severity"
          :value="comparison?.current?.high_severity_count || severityBreakdown?.high || 0"
          format="number"
          :delta="comparison?.deltas?.high_severity_count?.absolute"
          :is-positive-good="false"
          variant="danger"
          subtext="Critical complaints requiring immediate attention"
        />
        <KpiCard
          label="Escalation Rate"
          :value="comparison?.current?.escalation_rate || metrics.escalation_rate || 0"
          format="percent"
          :delta="comparison?.deltas?.escalation_rate?.absolute"
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
          label="FCR Rate"
          :value="comparison?.current?.fcr_rate || metrics.fcr_rate || 0"
          format="percent"
          :delta="comparison?.deltas?.fcr_rate?.absolute"
          :is-positive-good="true"
          :variant="(metrics.fcr_rate || 0) < 50 ? 'danger' : (metrics.fcr_rate || 0) < 65 ? 'warning' : 'success'"
        />
        <KpiCard
          label="Cost of Complaints"
          :value="comparison?.current?.total_cost || metrics.total_cost || 0"
          format="currency"
          :delta="comparison?.deltas?.total_cost?.absolute"
          :is-positive-good="false"
        />
        <KpiCard
          label="Cost per Complaint"
          :value="comparison?.current?.cost_per_call || 0"
          format="currency"
          :delta="comparison?.deltas?.cost_per_call?.absolute"
          :is-positive-good="false"
        />
      </div>

      <div class="grid-2" style="margin-top: 24px;">
        <!-- Severity Pyramid -->
        <div class="card">
          <div class="card-header">
            <span class="card-title">Severity Pyramid</span>
          </div>
          <div class="card-body">
            <SeverityPyramid
              v-if="severityBreakdown"
              :high="severityBreakdown.high"
              :medium="severityBreakdown.medium"
              :low="severityBreakdown.low"
            />
            <div v-else class="empty-state">Loading severity data...</div>
          </div>
        </div>

        <!-- Complaints by Category -->
        <div class="card">
          <div class="card-header">
            <span class="card-title">Top Pain Points</span>
          </div>
          <div class="card-body">
            <apexchart
              v-if="categoryBreakdown.length"
              type="bar"
              height="280"
              :options="topPainPointsOptions"
              :series="topPainPointsSeries"
            />
            <div v-else class="empty-state">No data</div>
          </div>
        </div>
      </div>

      <!-- Complaint Heatmap -->
      <div class="card" style="margin-top: 24px;">
        <div class="card-header">
          <span class="card-title">Complaint Heatmap: Product x Category</span>
        </div>
        <div class="card-body">
          <ComplaintHeatmap
            v-if="heatmapData && heatmapData.data?.length"
            :data="heatmapData.data"
            :categories="heatmapData.categories"
            @cell-click="handleHeatmapClick"
          />
          <div v-else class="empty-state">Loading heatmap data...</div>
        </div>
      </div>

      <!-- Complaint Trend -->
      <div class="card" style="margin-top: 24px;">
        <div class="card-header">
          <span class="card-title">Complaint Trend</span>
        </div>
        <div class="card-body">
          <apexchart
            v-if="trendData.labels.length"
            type="area"
            height="300"
            :options="trendChartOptions"
            :series="trendSeries"
          />
          <div v-else class="empty-state">No trend data</div>
        </div>
      </div>

      <!-- Category Breakdown Table -->
      <div class="card" style="margin-top: 24px;">
        <div class="card-header">
          <span class="card-title">Complaint Categories Detail</span>
        </div>

        <table v-if="categoryBreakdown.length" class="data-table">
          <thead>
            <tr>
              <th>Category</th>
              <th>Count</th>
              <th>% of Total</th>
              <th>Avg Handle Time</th>
              <th>FCR Rate</th>
              <th>Total Cost</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="cat in categoryBreakdown"
              :key="cat.label"
              @click="drillToCategory(cat.label)"
            >
              <td><span class="link">{{ cat.label }}</span></td>
              <td>{{ cat.count.toLocaleString() }}</td>
              <td>{{ cat.percentage }}%</td>
              <td>{{ cat.avg_handling_time_minutes }} min</td>
              <td>
                <span :class="['badge', cat.fcr_rate < 50 ? 'badge-red' : cat.fcr_rate < 65 ? 'badge-orange' : 'badge-green']">
                  {{ cat.fcr_rate }}%
                </span>
              </td>
              <td>${{ cat.total_cost.toLocaleString() }}</td>
            </tr>
          </tbody>
        </table>

        <div v-else class="empty-state">No complaint categories found</div>
      </div>

      <!-- Recent Complaints -->
      <div class="card" style="margin-top: 24px;">
        <div class="card-header">
          <span class="card-title">Recent Complaints</span>
          <button class="btn btn-primary btn-sm" @click="runRootCauseAnalysis" :disabled="analyzing">
            {{ analyzing ? 'Analyzing...' : 'Run Root Cause Analysis' }}
          </button>
        </div>

        <InteractionTable
          :interactions="recentComplaints"
          :total="recentComplaints.length"
          :loading="loadingComplaints"
          :show-pagination="false"
        />
      </div>

      <!-- Root Cause Results -->
      <div v-if="rootCauseResult" style="margin-top: 24px;">
        <RootCauseCards :result="rootCauseResult" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import BreadcrumbBar from '../components/BreadcrumbBar.vue'
import GlobalFilterBar from '../components/GlobalFilterBar.vue'
import InteractionTable from '../components/InteractionTable.vue'
import RootCauseCards from '../components/RootCauseCards.vue'
import KpiCard from '../components/KpiCard.vue'
import SeverityPyramid from '../components/SeverityPyramid.vue'
import ComplaintHeatmap from '../components/ComplaintHeatmap.vue'
import { useMainStore } from '../stores/main'
import { getMetrics, getTrends, getBreakdown, getInteractions, analyzeRootCauses, getMetricsComparison, getSeverityBreakdown, getComplaintHeatmap } from '../services/api'

const router = useRouter()
const store = useMainStore()

const loading = ref(false)
const loadingComplaints = ref(false)
const analyzing = ref(false)

const metrics = ref({})
const comparison = ref(null)
const trendData = ref({ labels: [], complaint_volume: [] })
const categoryBreakdown = ref([])
const severityData = ref([])
const severityBreakdown = ref(null)
const heatmapData = ref(null)
const recentComplaints = ref([])
const rootCauseResult = ref(null)

const maxSeverityCount = computed(() => {
  return Math.max(...severityData.value.map(s => s.count), 1)
})

// Chart options
const donutOptions = computed(() => ({
  chart: { toolbar: { show: false } },
  labels: categoryBreakdown.value.map(c => c.label),
  colors: ['#DC3545', '#F97316', '#EAB308', '#00843D', '#2563EB', '#8B5CF6', '#EC4899'],
  legend: { position: 'bottom' },
  dataLabels: { enabled: true, formatter: (val) => Math.round(val) + '%' }
}))

const donutSeries = computed(() => categoryBreakdown.value.map(c => c.count))

// Top Pain Points horizontal bar chart
const topPainPointsOptions = computed(() => ({
  chart: { toolbar: { show: false } },
  colors: ['#DC3545'],
  plotOptions: { bar: { horizontal: true, barHeight: '60%', borderRadius: 4 } },
  dataLabels: { enabled: true, formatter: (val) => val + '%' },
  xaxis: {
    categories: categoryBreakdown.value.slice(0, 6).map(c => c.label),
    max: 100
  },
  yaxis: { labels: { style: { fontSize: '12px' } } }
}))

const topPainPointsSeries = computed(() => [{
  name: 'Percentage',
  data: categoryBreakdown.value.slice(0, 6).map(c => c.percentage)
}])

const trendChartOptions = computed(() => ({
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
  yaxis: { title: { text: 'Complaints' } }
}))

const trendSeries = computed(() => [{
  name: 'Complaints',
  data: trendData.value.complaint_volume
}])

function getSeverityClass(severity) {
  switch (severity) {
    case 'High': return 'badge-red'
    case 'Medium': return 'badge-orange'
    case 'Low': return 'badge-yellow'
    default: return 'badge-gray'
  }
}

function getSeverityColor(severity) {
  switch (severity) {
    case 'High': return '#DC3545'
    case 'Medium': return '#F97316'
    case 'Low': return '#EAB308'
    default: return '#6C757D'
  }
}

async function loadData() {
  loading.value = true
  try {
    const filters = { ...store.globalFilters, complaintsOnly: true }

    // Calculate date ranges for comparison
    const toDate = filters.to || new Date().toISOString().split('T')[0]
    const fromDate = filters.from || new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0]

    const [metricsData, trendsData, categoryData, comparisonData, severityData2, heatmapResult] = await Promise.all([
      getMetrics(filters),
      getTrends(filters, 'daily'),
      getBreakdown(filters, 'complaint_category'),
      getMetricsComparison(fromDate, toDate, { ...filters, complaintsOnly: true }).catch(() => null),
      getSeverityBreakdown(store.globalFilters).catch(() => null),
      getComplaintHeatmap(store.globalFilters).catch(() => null)
    ])

    metrics.value = metricsData
    trendData.value = trendsData
    comparison.value = comparisonData
    severityBreakdown.value = severityData2
    heatmapData.value = heatmapResult

    // Process category breakdown
    const total = categoryData.data.reduce((sum, c) => sum + c.count, 0)
    categoryBreakdown.value = categoryData.data.map(c => ({
      ...c,
      percentage: Math.round(c.count / total * 100)
    }))

    // Get severity breakdown (legacy for bar chart)
    const severityResult = await getBreakdown(filters, 'complaint_severity')
    severityData.value = severityResult.data

    await loadRecentComplaints()
  } catch (error) {
    console.error('Failed to load data:', error)
  } finally {
    loading.value = false
  }
}

function handleHeatmapClick({ product, category, count }) {
  if (count > 0) {
    // Navigate to interactions filtered by product and complaint category
    const params = new URLSearchParams()
    params.set('product', product)
    params.set('complaint_category', category)
    router.push(`/interactions?${params.toString()}`)
  }
}

async function loadRecentComplaints() {
  loadingComplaints.value = true
  try {
    const filters = { ...store.globalFilters, complaintsOnly: true }
    const result = await getInteractions(filters, 1, 20)
    recentComplaints.value = result.data
  } catch (error) {
    console.error('Failed to load complaints:', error)
  } finally {
    loadingComplaints.value = false
  }
}

async function runRootCauseAnalysis() {
  analyzing.value = true
  try {
    const filters = { ...store.globalFilters, complaints_only: true }
    const result = await analyzeRootCauses({ filters })
    rootCauseResult.value = result
    store.setLastRootCauseResult(result)
  } catch (error) {
    console.error('Failed to analyze:', error)
  } finally {
    analyzing.value = false
  }
}

function drillToCategory(category) {
  // Navigate to interactions filtered by this complaint category
  router.push(`/interactions?complaint_category=${encodeURIComponent(category)}`)
}

function handleFilterChange() {
  rootCauseResult.value = null
  loadData()
}

onMounted(() => {
  loadData()
})
</script>
