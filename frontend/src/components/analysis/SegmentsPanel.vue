<template>
  <div class="segments-panel">
    <div class="panel-header">
      <div class="segment-selector">
        <label>Segment by:</label>
        <select v-model="selectedSegment" @change="loadBreakdown">
          <option value="region">Region</option>
          <option value="channel">Channel</option>
          <option value="customer_segment">Customer Segment</option>
          <option value="call_reason">Call Reason</option>
          <option value="root_cause_label">Root Cause</option>
          <option value="product">Product</option>
          <option value="line_of_business">Line of Business</option>
        </select>
      </div>
    </div>

    <div v-if="loading" class="loading">Loading segment breakdown...</div>

    <div v-else-if="breakdownData.length" class="segment-content">
      <!-- Horizontal Bar Chart -->
      <div class="chart-section">
        <apexchart
          type="bar"
          height="300"
          :options="chartOptions"
          :series="chartSeries"
        />
      </div>

      <!-- Data Table -->
      <div class="table-section">
        <table class="data-table">
          <thead>
            <tr>
              <th>{{ segmentLabels[selectedSegment] }}</th>
              <th>Interactions</th>
              <th>Complaints</th>
              <th>Complaint Rate</th>
              <th>FCR Rate</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in breakdownData" :key="item.label">
              <td>{{ item.label }}</td>
              <td>{{ item.count.toLocaleString() }}</td>
              <td>{{ item.complaint_count.toLocaleString() }}</td>
              <td>
                <span :class="['badge', item.complaint_rate > 25 ? 'badge-red' : item.complaint_rate > 15 ? 'badge-orange' : 'badge-green']">
                  {{ item.complaint_rate }}%
                </span>
              </td>
              <td>
                <span :class="['badge', item.fcr_rate < 60 ? 'badge-red' : item.fcr_rate < 75 ? 'badge-orange' : 'badge-green']">
                  {{ item.fcr_rate }}%
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <div v-else class="empty-state">
      No segment data available
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { getBreakdown } from '../../services/api'

const props = defineProps({
  filters: {
    type: Object,
    default: () => ({})
  }
})

const selectedSegment = ref('region')
const breakdownData = ref([])
const loading = ref(false)

const segmentLabels = {
  region: 'Region',
  channel: 'Channel',
  customer_segment: 'Customer Segment',
  call_reason: 'Call Reason',
  root_cause_label: 'Root Cause',
  product: 'Product',
  line_of_business: 'Line of Business'
}

const chartOptions = computed(() => ({
  chart: {
    type: 'bar',
    toolbar: { show: false }
  },
  plotOptions: {
    bar: {
      horizontal: true,
      barHeight: '70%',
      borderRadius: 4
    }
  },
  colors: ['#00843D', '#DC3545'],
  dataLabels: { enabled: false },
  xaxis: {
    categories: breakdownData.value.map(b => b.label.length > 20 ? b.label.slice(0, 20) + '...' : b.label)
  },
  legend: { position: 'top' },
  grid: {
    borderColor: '#E5E7EB'
  }
}))

const chartSeries = computed(() => [
  { name: 'Total Interactions', data: breakdownData.value.map(b => b.count) },
  { name: 'Complaints', data: breakdownData.value.map(b => b.complaint_count) }
])

async function loadBreakdown() {
  loading.value = true
  try {
    const result = await getBreakdown(props.filters, selectedSegment.value)
    breakdownData.value = result.data
  } catch (error) {
    console.error('Failed to load breakdown:', error)
    breakdownData.value = []
  } finally {
    loading.value = false
  }
}

watch(() => props.filters, () => {
  loadBreakdown()
}, { deep: true })

onMounted(() => {
  loadBreakdown()
})
</script>

<style scoped>
.segments-panel {
  padding: 16px;
}

.panel-header {
  margin-bottom: 16px;
}

.segment-selector {
  display: flex;
  align-items: center;
  gap: 8px;
}

.segment-selector label {
  font-size: 13px;
  color: var(--td-gray-600);
}

.segment-selector select {
  padding: 6px 10px;
  border: 1px solid var(--td-gray-300);
  border-radius: 6px;
  font-size: 13px;
  background: white;
}

.segment-content {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.chart-section {
  background: var(--td-gray-50);
  border-radius: 8px;
  padding: 16px;
}

.table-section {
  overflow-x: auto;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
}

.data-table th,
.data-table td {
  padding: 10px 12px;
  text-align: left;
  border-bottom: 1px solid var(--td-gray-200);
}

.data-table th {
  background: var(--td-gray-50);
  font-weight: 600;
  color: var(--td-gray-700);
}

.data-table tbody tr:hover {
  background: var(--td-gray-50);
}

.badge {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 10px;
  font-size: 12px;
  font-weight: 500;
}

.badge-green {
  background: #D1FAE5;
  color: #047857;
}

.badge-orange {
  background: #FEF3C7;
  color: #B45309;
}

.badge-red {
  background: #FEE2E2;
  color: #B91C1C;
}

.loading, .empty-state {
  padding: 40px;
  text-align: center;
  color: var(--td-gray-500);
  font-size: 13px;
}
</style>
