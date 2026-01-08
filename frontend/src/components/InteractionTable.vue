<template>
  <div class="card">
    <div class="card-header">
      <span class="card-title">{{ title }}</span>
      <span style="font-size: 13px; color: var(--td-gray-600);">{{ total }} interactions</span>
    </div>

    <div v-if="loading" class="loading">Loading interactions...</div>

    <div v-else-if="!interactions.length" class="empty-state">
      No interactions found
    </div>

    <template v-else>
      <table class="data-table">
        <thead>
          <tr>
            <th>Timestamp</th>
            <th>Agent</th>
            <th>Call Reason</th>
            <th>Product</th>
            <th>Complaint</th>
            <th>Handle Time</th>
            <th>Resolved</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="interaction in interactions"
            :key="interaction.interaction_id"
            @click="handleRowClick(interaction)"
          >
            <td>{{ formatTimestamp(interaction.timestamp) }}</td>
            <td>{{ interaction.agent_name }}</td>
            <td>{{ interaction.call_reason }}</td>
            <td>{{ truncate(interaction.product, 25) }}</td>
            <td>
              <span v-if="interaction.is_complaint" class="badge badge-red">
                {{ interaction.complaint_severity }}
              </span>
              <span v-else class="badge badge-gray">No</span>
            </td>
            <td>{{ Math.round(interaction.handling_time_seconds / 60) }} min</td>
            <td>
              <span :class="['badge', interaction.resolved_on_first_contact ? 'badge-green' : 'badge-orange']">
                {{ interaction.resolved_on_first_contact ? 'Yes' : 'No' }}
              </span>
            </td>
          </tr>
        </tbody>
      </table>

      <div class="pagination" v-if="showPagination && totalPages > 1">
        <button @click="emit('page-change', currentPage - 1)" :disabled="currentPage <= 1">
          ← Previous
        </button>
        <span class="page-info">Page {{ currentPage }} of {{ totalPages }}</span>
        <button @click="emit('page-change', currentPage + 1)" :disabled="currentPage >= totalPages">
          Next →
        </button>
      </div>
    </template>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'

const props = defineProps({
  title: {
    type: String,
    default: 'Interactions'
  },
  interactions: {
    type: Array,
    default: () => []
  },
  total: {
    type: Number,
    default: 0
  },
  currentPage: {
    type: Number,
    default: 1
  },
  totalPages: {
    type: Number,
    default: 1
  },
  loading: {
    type: Boolean,
    default: false
  },
  showPagination: {
    type: Boolean,
    default: true
  }
})

const emit = defineEmits(['page-change', 'row-click'])
const router = useRouter()

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

function handleRowClick(interaction) {
  emit('row-click', interaction)
  router.push(`/interactions/${interaction.interaction_id}`)
}
</script>
