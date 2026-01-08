<template>
  <div>
    <BreadcrumbBar :crumbs="breadcrumbs" />

    <div class="page-header">
      <h1 class="page-title">Agent Performance</h1>
      <p class="page-subtitle">Monitor agent metrics and identify coaching opportunities</p>
    </div>

    <div class="filter-bar">
      <div class="filter-group">
        <label>Date Range</label>
        <select v-model="dateRange" @change="handleDateRangeChange">
          <option value="7">Last 7 Days</option>
          <option value="30">Last 30 Days</option>
          <option value="60">Last 60 Days</option>
          <option value="90">Last 90 Days</option>
        </select>
      </div>

      <div class="filter-group">
        <label>Region</label>
        <select v-model="selectedRegion" @change="loadData">
          <option value="">All Regions</option>
          <option v-for="region in options.regions" :key="region" :value="region">{{ region }}</option>
        </select>
      </div>

      <div class="filter-group">
        <label>Team Leader</label>
        <select v-model="selectedTeamLeader" @change="loadData">
          <option value="">All Leaders</option>
          <option v-for="leader in availableLeaders" :key="leader" :value="leader">{{ leader }}</option>
        </select>
      </div>
    </div>

    <div class="page-content">
      <!-- Enhanced KPI Summary - Row 1 -->
      <div class="kpi-grid-enhanced">
        <KpiCard
          label="Active Agents"
          :value="agentPerformance.length"
          format="number"
          variant="highlight"
        />
        <KpiCard
          label="Agents At Risk"
          :value="agentsAtRisk"
          format="number"
          variant="danger"
          subtext="Complaint rate > 1.5x avg"
          :clickable="true"
          @click="filterToAtRisk"
        />
        <KpiCard
          label="Top Performers"
          :value="topPerformersCount"
          format="number"
          variant="success"
          subtext="FCR > 85%"
        />
        <KpiCard
          label="Avg Complaint Rate"
          :value="parseFloat(avgComplaintRate)"
          format="percent"
          :is-positive-good="false"
          :variant="parseFloat(avgComplaintRate) > 25 ? 'danger' : parseFloat(avgComplaintRate) > 18 ? 'warning' : 'default'"
        />
      </div>

      <!-- Enhanced KPI Summary - Row 2 -->
      <div class="kpi-grid-enhanced" style="margin-top: 16px;">
        <KpiCard
          label="Avg FCR Rate"
          :value="parseFloat(avgFcrRate)"
          format="percent"
          :is-positive-good="true"
          :variant="parseFloat(avgFcrRate) < 60 ? 'danger' : parseFloat(avgFcrRate) < 75 ? 'warning' : 'success'"
        />
        <KpiCard
          label="Avg Handle Time"
          :value="avgHandleTime"
          format="time"
          :is-positive-good="false"
        />
        <KpiCard
          label="Regional Variance"
          :value="regionalVariance"
          format="percent"
          subtext="Best vs worst region gap"
        />
        <KpiCard
          label="Calls per Agent/Day"
          :value="callsPerAgentPerDay"
          format="decimal"
          tooltip="Average daily workload per agent"
        />
      </div>

      <!-- Performance Quadrant -->
      <div class="card" style="margin-top: 24px;">
        <div class="card-header">
          <span class="card-title">Performance Quadrant</span>
          <span style="font-size: 12px; color: var(--td-gray-500);">Click on agent dots to view details</span>
        </div>
        <div class="card-body">
          <PerformanceQuadrant
            v-if="agentPerformance.length"
            :agents="agentPerformance"
            :fcr-threshold="75"
            :complaint-threshold="parseFloat(avgComplaintRate) * 1.2"
            @agent-click="viewAgentProfile"
          />
          <div v-else class="empty-state">Loading agent data...</div>
        </div>
      </div>

      <div class="grid-2" style="margin-top: 24px;">
        <!-- Top Performers -->
        <div class="card">
          <div class="card-header">
            <span class="card-title">Top Performers (FCR)</span>
          </div>
          <div class="card-body">
            <div v-if="topPerformers.length" style="display: flex; flex-direction: column; gap: 12px;">
              <div
                v-for="(agent, i) in topPerformers"
                :key="agent.agent_id"
                style="display: flex; align-items: center; gap: 12px; padding: 8px; background: var(--td-gray-100); border-radius: 6px; cursor: pointer;"
                @click="viewAgentProfile(agent.agent_id)"
              >
                <span style="width: 24px; height: 24px; background: var(--td-green); color: white; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 12px; font-weight: 600;">
                  {{ i + 1 }}
                </span>
                <div style="flex: 1;">
                  <div style="font-weight: 600;">{{ agent.agent_name }}</div>
                  <div style="font-size: 12px; color: var(--td-gray-600);">{{ agent.team_leader }} · {{ agent.region }}</div>
                </div>
                <span class="badge badge-green">{{ agent.fcr_rate }}% FCR</span>
              </div>
            </div>
            <div v-else class="empty-state">No data</div>
          </div>
        </div>

        <!-- Needs Improvement -->
        <div class="card">
          <div class="card-header">
            <span class="card-title">Needs Coaching (High Complaints)</span>
          </div>
          <div class="card-body">
            <div v-if="needsImprovement.length" style="display: flex; flex-direction: column; gap: 12px;">
              <div
                v-for="(agent, i) in needsImprovement"
                :key="agent.agent_id"
                style="display: flex; align-items: center; gap: 12px; padding: 8px; background: var(--td-red-light); border-radius: 6px; cursor: pointer;"
                @click="viewAgentProfile(agent.agent_id)"
              >
                <span style="width: 24px; height: 24px; background: var(--td-red); color: white; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 12px; font-weight: 600;">
                  {{ i + 1 }}
                </span>
                <div style="flex: 1;">
                  <div style="font-weight: 600;">{{ agent.agent_name }}</div>
                  <div style="font-size: 12px; color: var(--td-gray-600);">{{ agent.team_leader }} · {{ agent.tenure_band }}</div>
                </div>
                <span class="badge badge-red">{{ agent.complaint_rate }}% Complaints</span>
              </div>
            </div>
            <div v-else class="empty-state">All agents performing well</div>
          </div>
        </div>
      </div>

      <!-- Tenure Comparison -->
      <div class="card" style="margin-top: 24px;">
        <div class="card-header">
          <span class="card-title">Performance by Tenure</span>
        </div>
        <div class="card-body">
          <apexchart
            v-if="tenureData.length"
            type="bar"
            height="250"
            :options="tenureChartOptions"
            :series="tenureSeries"
          />
          <div v-else class="empty-state">No tenure data</div>
        </div>
      </div>

      <!-- Performance by Region Chart -->
      <div class="card" style="margin-top: 24px;">
        <div class="card-header">
          <span class="card-title">Performance by Region</span>
        </div>
        <div class="card-body">
          <apexchart
            v-if="regionData.length"
            type="bar"
            height="300"
            :options="regionChartOptions"
            :series="regionSeries"
          />
          <div v-else class="empty-state">No data</div>
        </div>
      </div>

      <!-- Full Agent Table -->
      <div class="card" style="margin-top: 24px;">
        <div class="card-header">
          <span class="card-title">All Agents</span>
          <span style="font-size: 13px; color: var(--td-gray-600);">Sorted by complaint rate (highest first)</span>
        </div>

        <div v-if="loading" class="loading">Loading agent data...</div>

        <table v-else-if="agentPerformance.length" class="data-table">
          <thead>
            <tr>
              <th>Agent</th>
              <th>Region</th>
              <th>Team Leader</th>
              <th>Tenure</th>
              <th>Interactions</th>
              <th>Complaints</th>
              <th>Complaint Rate</th>
              <th>Avg Handle Time</th>
              <th>FCR Rate</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="agent in agentPerformance"
              :key="agent.agent_id"
              @click="viewAgentDetail(agent)"
            >
              <td>
                <span class="link">{{ agent.agent_name }}</span>
                <br><small style="color: var(--td-gray-500);">{{ agent.agent_id }}</small>
              </td>
              <td>{{ agent.region }}</td>
              <td>{{ agent.team_leader }}</td>
              <td>{{ agent.tenure_band }}</td>
              <td>{{ agent.interaction_count.toLocaleString() }}</td>
              <td>{{ agent.complaint_count }}</td>
              <td>
                <span :class="['badge', getComplaintRateClass(agent.complaint_rate)]">
                  {{ agent.complaint_rate }}%
                </span>
              </td>
              <td>{{ agent.avg_handling_time_minutes }} min</td>
              <td>
                <span :class="['badge', getFcrRateClass(agent.fcr_rate)]">
                  {{ agent.fcr_rate }}%
                </span>
              </td>
            </tr>
          </tbody>
        </table>

        <div v-else class="empty-state">No agent data available</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import BreadcrumbBar from '../components/BreadcrumbBar.vue'
import KpiCard from '../components/KpiCard.vue'
import PerformanceQuadrant from '../components/PerformanceQuadrant.vue'
import { useMainStore } from '../stores/main'
import { getAgentPerformance, getBreakdown } from '../services/api'

const router = useRouter()
const store = useMainStore()
const options = store.options

const loading = ref(false)
const dateRange = ref('30')
const selectedRegion = ref('')
const selectedTeamLeader = ref('')

const agentPerformance = ref([])
const regionData = ref([])

const breadcrumbs = computed(() => {
  const crumbs = [{ label: 'Agent Performance' }]
  if (selectedRegion.value) {
    crumbs.push({ label: selectedRegion.value })
  }
  if (selectedTeamLeader.value) {
    crumbs.push({ label: selectedTeamLeader.value })
  }
  return crumbs
})

const availableLeaders = computed(() => {
  if (selectedRegion.value && options.teamLeaders[selectedRegion.value]) {
    return options.teamLeaders[selectedRegion.value]
  }
  return options.allTeamLeaders
})

const totalInteractions = computed(() => {
  return agentPerformance.value.reduce((sum, a) => sum + a.interaction_count, 0)
})

const avgComplaintRate = computed(() => {
  if (!agentPerformance.value.length) return 0
  const total = agentPerformance.value.reduce((sum, a) => sum + a.complaint_rate, 0)
  return (total / agentPerformance.value.length).toFixed(1)
})

const avgFcrRate = computed(() => {
  if (!agentPerformance.value.length) return 0
  const total = agentPerformance.value.reduce((sum, a) => sum + a.fcr_rate, 0)
  return (total / agentPerformance.value.length).toFixed(1)
})

const topPerformers = computed(() => {
  return [...agentPerformance.value]
    .filter(a => a.interaction_count >= 10)
    .sort((a, b) => b.fcr_rate - a.fcr_rate)
    .slice(0, 5)
})

const needsImprovement = computed(() => {
  return [...agentPerformance.value]
    .filter(a => a.interaction_count >= 10 && a.complaint_rate > 20)
    .sort((a, b) => b.complaint_rate - a.complaint_rate)
    .slice(0, 5)
})

// New KPI computed properties
const agentsAtRisk = computed(() => {
  const avgRate = parseFloat(avgComplaintRate.value)
  const threshold = avgRate * 1.5
  return agentPerformance.value.filter(a => a.complaint_rate > threshold && a.interaction_count >= 10).length
})

const topPerformersCount = computed(() => {
  return agentPerformance.value.filter(a => a.fcr_rate >= 85 && a.interaction_count >= 10).length
})

const avgHandleTime = computed(() => {
  if (!agentPerformance.value.length) return 0
  const total = agentPerformance.value.reduce((sum, a) => sum + (a.avg_handling_time_minutes || 0), 0)
  return Math.round(total / agentPerformance.value.length * 10) / 10
})

const regionalVariance = computed(() => {
  if (!regionData.value.length) return 0
  const rates = regionData.value.map(r => r.complaint_rate || 0)
  const max = Math.max(...rates)
  const min = Math.min(...rates)
  return Math.round((max - min) * 10) / 10
})

const callsPerAgentPerDay = computed(() => {
  if (!agentPerformance.value.length) return 0
  const days = parseInt(dateRange.value)
  const totalCalls = agentPerformance.value.reduce((sum, a) => sum + a.interaction_count, 0)
  const agentCount = agentPerformance.value.length
  return Math.round(totalCalls / agentCount / days * 10) / 10
})

// Tenure data for bar chart
const tenureData = computed(() => {
  const tenureBands = ['< 6 months', '6-24 months', '2+ years']
  const result = []

  tenureBands.forEach(band => {
    const agents = agentPerformance.value.filter(a => a.tenure_band === band)
    if (agents.length > 0) {
      const avgFcr = Math.round(agents.reduce((sum, a) => sum + a.fcr_rate, 0) / agents.length * 10) / 10
      const avgCr = Math.round(agents.reduce((sum, a) => sum + a.complaint_rate, 0) / agents.length * 10) / 10
      result.push({
        label: band,
        agentCount: agents.length,
        fcr_rate: avgFcr,
        complaint_rate: avgCr
      })
    }
  })

  return result
})

const tenureChartOptions = computed(() => ({
  chart: { toolbar: { show: false }, stacked: false },
  colors: ['#00843D', '#DC3545'],
  plotOptions: { bar: { horizontal: true, barHeight: '60%', borderRadius: 4 } },
  dataLabels: { enabled: true, formatter: (val) => val + '%' },
  xaxis: {
    categories: tenureData.value.map(t => t.label),
    max: 100
  },
  yaxis: { labels: { style: { fontSize: '12px' } } },
  legend: { position: 'top' },
  tooltip: {
    y: { formatter: (val) => val + '%' }
  }
}))

const tenureSeries = computed(() => [
  { name: 'FCR Rate', data: tenureData.value.map(t => t.fcr_rate) },
  { name: 'Complaint Rate', data: tenureData.value.map(t => t.complaint_rate) }
])

// Region chart
const regionChartOptions = computed(() => ({
  chart: { toolbar: { show: false }, stacked: false },
  colors: ['#00843D', '#DC3545', '#2563EB'],
  plotOptions: { bar: { horizontal: false, columnWidth: '60%' } },
  dataLabels: { enabled: false },
  xaxis: { categories: regionData.value.map(r => r.label) },
  yaxis: [
    { title: { text: 'Interactions' } },
    { opposite: true, title: { text: 'Rate (%)' } }
  ],
  legend: { position: 'top' }
}))

const regionSeries = computed(() => [
  { name: 'Interactions', type: 'column', data: regionData.value.map(r => r.count) },
  { name: 'Complaint Rate', type: 'line', data: regionData.value.map(r => r.complaint_rate) },
  { name: 'FCR Rate', type: 'line', data: regionData.value.map(r => r.fcr_rate) }
])

function getComplaintRateClass(rate) {
  if (rate > 30) return 'badge-red'
  if (rate > 20) return 'badge-orange'
  return 'badge-green'
}

function getFcrRateClass(rate) {
  if (rate < 60) return 'badge-red'
  if (rate < 75) return 'badge-orange'
  return 'badge-green'
}

function calculateDateRange(days) {
  const to = new Date()
  const from = new Date()
  from.setDate(from.getDate() - days)
  return {
    from: from.toISOString().split('T')[0],
    to: to.toISOString().split('T')[0]
  }
}

function handleDateRangeChange() {
  loadData()
}

async function loadData() {
  loading.value = true
  try {
    const { from, to } = calculateDateRange(parseInt(dateRange.value))

    const filters = {
      from,
      to,
      region: selectedRegion.value,
      teamLeader: selectedTeamLeader.value
    }

    const [agentData, regionBreakdown] = await Promise.all([
      getAgentPerformance(filters),
      getBreakdown({ from, to, complaintsOnly: false }, 'region')
    ])

    agentPerformance.value = agentData.data
    regionData.value = regionBreakdown.data
  } catch (error) {
    console.error('Failed to load data:', error)
  } finally {
    loading.value = false
  }
}

function viewAgentDetail(agent) {
  store.setGlobalFilters({ agentId: agent.agent_id })
  router.push('/interactions')
}

function filterToAtRisk() {
  // Filter the table to show only at-risk agents
  const avgRate = parseFloat(avgComplaintRate.value)
  const threshold = avgRate * 1.5
  const atRiskAgents = agentPerformance.value.filter(a => a.complaint_rate > threshold && a.interaction_count >= 10)
  // For now, just scroll to table - could implement actual filtering
  const table = document.querySelector('.data-table')
  if (table) {
    table.scrollIntoView({ behavior: 'smooth' })
  }
}

function viewAgentProfile(agentId) {
  // Navigate to agent's interactions
  store.setGlobalFilters({ agentId: agentId })
  router.push('/interactions')
}

onMounted(() => {
  // Check if there's an agent filter set
  if (store.globalFilters.agentId) {
    // Could show agent-specific view
  }
  loadData()
})
</script>
