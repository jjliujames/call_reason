<template>
  <div class="products-panel">
    <div v-if="loading" class="loading">Loading product breakdown...</div>

    <div v-else-if="breakdownData.length" class="products-content">
      <!-- Chart Section -->
      <div class="chart-section">
        <apexchart
          type="bar"
          height="350"
          :options="chartOptions"
          :series="chartSeries"
        />
      </div>

      <!-- Data Table -->
      <div class="table-section">
        <table class="data-table">
          <thead>
            <tr>
              <th>Product</th>
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
              v-for="item in breakdownData"
              :key="item.label"
              @click="selectProduct(item.label)"
              class="clickable-row"
            >
              <td class="product-name">{{ item.label }}</td>
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
      </div>
    </div>

    <div v-else class="empty-state">
      No product data available
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

const emit = defineEmits(['select-product'])

const breakdownData = ref([])
const loading = ref(false)

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
    categories: breakdownData.value.slice(0, 10).map(b => b.label.length > 25 ? b.label.slice(0, 25) + '...' : b.label)
  },
  legend: { position: 'top' },
  grid: {
    borderColor: '#E5E7EB'
  }
}))

const chartSeries = computed(() => [
  { name: 'Total Interactions', data: breakdownData.value.slice(0, 10).map(b => b.count) },
  { name: 'Complaints', data: breakdownData.value.slice(0, 10).map(b => b.complaint_count) }
])

async function loadBreakdown() {
  loading.value = true
  try {
    const result = await getBreakdown(props.filters, 'product')
    breakdownData.value = result.data
  } catch (error) {
    console.error('Failed to load breakdown:', error)
    breakdownData.value = []
  } finally {
    loading.value = false
  }
}

function selectProduct(productLabel) {
  emit('select-product', productLabel)
}

watch(() => props.filters, () => {
  loadBreakdown()
}, { deep: true })

onMounted(() => {
  loadBreakdown()
})
</script>

<style scoped>
.products-panel {
  padding: 16px;
}

.products-content {
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

.clickable-row {
  cursor: pointer;
  transition: background 0.15s;
}

.clickable-row:hover {
  background: var(--td-gray-50);
}

.product-name {
  font-weight: 500;
  color: var(--td-green);
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
