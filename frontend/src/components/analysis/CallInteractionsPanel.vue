<template>
  <div class="interactions-panel">
    <div class="panel-header">
      <div class="header-info">
        <span class="result-count">{{ total.toLocaleString() }} interactions</span>
        <span v-if="hasFilters" class="filter-hint">filtered by taxonomy selection</span>
      </div>
      <div class="panel-actions">
        <select v-model="sortBy" class="sort-select">
          <option value="timestamp">Sort by Date</option>
          <option value="handling_time">Sort by Handle Time</option>
          <option value="complaint_severity">Sort by Severity</option>
        </select>
      </div>
    </div>

    <div v-if="loading" class="loading">Loading interactions...</div>

    <div v-else-if="interactions.length" class="interactions-content">
      <!-- Interactions Table -->
      <table class="data-table">
        <thead>
          <tr>
            <th>Timestamp</th>
            <th>Agent</th>
            <th>Call Reason</th>
            <th>Product</th>
            <th>Channel</th>
            <th>Complaint</th>
            <th>Handle Time</th>
            <th>FCR</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="item in interactions"
            :key="item.interaction_id"
            class="interaction-row"
            @click="goToDetail(item.interaction_id)"
          >
            <td>{{ formatTimestamp(item.timestamp) }}</td>
            <td>
              <div class="agent-cell">
                <span class="agent-name">{{ item.agent_name }}</span>
                <span class="agent-id">{{ item.agent_id }}</span>
              </div>
            </td>
            <td>{{ truncate(item.call_reason, 25) }}</td>
            <td>{{ truncate(item.product, 20) }}</td>
            <td>
              <span class="badge badge-blue">{{ item.channel }}</span>
            </td>
            <td>
              <span v-if="item.is_complaint" :class="['badge', severityClass(item.complaint_severity)]">
                {{ item.complaint_severity }}
              </span>
              <span v-else class="badge badge-gray">No</span>
            </td>
            <td>{{ Math.round(item.handling_time_seconds / 60) }} min</td>
            <td>
              <span :class="['badge', item.resolved_on_first_contact ? 'badge-green' : 'badge-orange']">
                {{ item.resolved_on_first_contact ? 'Yes' : 'No' }}
              </span>
            </td>
          </tr>
        </tbody>
      </table>

      <!-- Pagination -->
      <div class="pagination">
        <button
          class="page-btn"
          :disabled="currentPage === 1"
          @click="goToPage(currentPage - 1)"
        >
          Previous
        </button>
        <div class="page-info">
          Page {{ currentPage }} of {{ totalPages }}
        </div>
        <button
          class="page-btn"
          :disabled="currentPage >= totalPages"
          @click="goToPage(currentPage + 1)"
        >
          Next
        </button>
      </div>
    </div>

    <div v-else class="empty-state">
      No interactions found for the selected filters
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { getInteractions } from '../../services/api'

const props = defineProps({
  filters: {
    type: Object,
    default: () => ({})
  }
})

const router = useRouter()

const interactions = ref([])
const loading = ref(false)
const currentPage = ref(1)
const pageSize = ref(15)
const total = ref(0)
const sortBy = ref('timestamp')

const totalPages = computed(() => Math.ceil(total.value / pageSize.value) || 1)

const hasFilters = computed(() => {
  return props.filters.lineOfBusiness || props.filters.callReason ||
         props.filters.product || props.filters.region
})

async function loadInteractions() {
  loading.value = true
  try {
    const result = await getInteractions(props.filters, currentPage.value, pageSize.value)
    interactions.value = result.data
    total.value = result.total
  } catch (error) {
    console.error('Failed to load interactions:', error)
    interactions.value = []
    total.value = 0
  } finally {
    loading.value = false
  }
}

function goToPage(page) {
  if (page >= 1 && page <= totalPages.value) {
    currentPage.value = page
    loadInteractions()
  }
}

function goToDetail(id) {
  router.push(`/interactions/${id}`)
}

function formatTimestamp(ts) {
  const date = new Date(ts)
  return date.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

function truncate(str, maxLength) {
  if (!str) return ''
  return str.length > maxLength ? str.slice(0, maxLength) + '...' : str
}

function severityClass(severity) {
  switch (severity) {
    case 'High': return 'badge-red'
    case 'Medium': return 'badge-orange'
    case 'Low': return 'badge-yellow'
    default: return 'badge-gray'
  }
}

watch(() => props.filters, () => {
  currentPage.value = 1
  loadInteractions()
}, { deep: true })

watch(sortBy, () => {
  loadInteractions()
})

onMounted(() => {
  loadInteractions()
})
</script>

<style scoped>
.interactions-panel {
  padding: 16px;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.header-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.result-count {
  font-size: 14px;
  font-weight: 600;
  color: var(--td-gray-800);
}

.filter-hint {
  font-size: 12px;
  color: var(--td-gray-500);
  font-style: italic;
}

.sort-select {
  padding: 6px 10px;
  border: 1px solid var(--td-gray-300);
  border-radius: 6px;
  font-size: 13px;
  background: white;
}

.interactions-content {
  display: flex;
  flex-direction: column;
  gap: 16px;
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
  white-space: nowrap;
}

.interaction-row {
  cursor: pointer;
  transition: background 0.15s;
}

.interaction-row:hover {
  background: var(--td-gray-50);
}

.agent-cell {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.agent-name {
  font-weight: 500;
  color: var(--td-gray-800);
}

.agent-id {
  font-size: 11px;
  color: var(--td-gray-500);
}

.badge {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 10px;
  font-size: 11px;
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

.badge-yellow {
  background: #FEF9C3;
  color: #A16207;
}

.badge-red {
  background: #FEE2E2;
  color: #B91C1C;
}

.badge-blue {
  background: #DBEAFE;
  color: #1D4ED8;
}

.badge-gray {
  background: var(--td-gray-100);
  color: var(--td-gray-600);
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 16px;
  padding: 16px 0;
  border-top: 1px solid var(--td-gray-200);
}

.page-btn {
  padding: 8px 16px;
  font-size: 13px;
  font-weight: 500;
  background: white;
  border: 1px solid var(--td-gray-300);
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.15s;
}

.page-btn:hover:not(:disabled) {
  background: var(--td-gray-50);
  border-color: var(--td-gray-400);
}

.page-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-info {
  font-size: 13px;
  color: var(--td-gray-600);
}

.loading, .empty-state {
  padding: 40px;
  text-align: center;
  color: var(--td-gray-500);
  font-size: 13px;
}
</style>
