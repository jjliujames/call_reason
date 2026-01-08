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
            <th v-if="selectable" class="checkbox-col">
              <input
                type="checkbox"
                :checked="allSelected"
                :indeterminate="someSelected && !allSelected"
                @change="toggleSelectAll"
              />
            </th>
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
            :class="{ 'selected-row': isSelected(interaction.interaction_id) }"
            @click="handleRowClick($event, interaction)"
          >
            <td v-if="selectable" class="checkbox-col" @click.stop>
              <input
                type="checkbox"
                :checked="isSelected(interaction.interaction_id)"
                @change="toggleSelect(interaction)"
              />
            </td>
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

    <!-- Floating Action Bar -->
    <Teleport to="body">
      <Transition name="slide-up">
        <div v-if="selectable && selectedIds.length > 0" class="selection-action-bar">
          <div class="selection-info">
            <span class="selection-count">{{ selectedIds.length }}</span>
            <span>interactions selected</span>
          </div>
          <div class="selection-actions">
            <button class="btn btn-secondary btn-sm" @click="clearSelection">
              Clear Selection
            </button>
            <button class="btn btn-primary btn-sm" @click="analyzeSelected">
              Analyze Root Causes
            </button>
          </div>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
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
  },
  selectable: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['page-change', 'row-click', 'selection-change', 'analyze-selected'])
const router = useRouter()

// Selection state
const selectedIds = ref([])

// Computed
const allSelected = computed(() => {
  return props.interactions.length > 0 && selectedIds.value.length === props.interactions.length
})

const someSelected = computed(() => {
  return selectedIds.value.length > 0
})

// Watch for interaction changes to clear invalid selections
watch(() => props.interactions, () => {
  const validIds = new Set(props.interactions.map(i => i.interaction_id))
  selectedIds.value = selectedIds.value.filter(id => validIds.has(id))
}, { deep: true })

// Methods
function isSelected(id) {
  return selectedIds.value.includes(id)
}

function toggleSelect(interaction) {
  const id = interaction.interaction_id
  const index = selectedIds.value.indexOf(id)
  if (index === -1) {
    selectedIds.value.push(id)
  } else {
    selectedIds.value.splice(index, 1)
  }
  emit('selection-change', selectedIds.value, getSelectedInteractions())
}

function toggleSelectAll() {
  if (allSelected.value) {
    selectedIds.value = []
  } else {
    selectedIds.value = props.interactions.map(i => i.interaction_id)
  }
  emit('selection-change', selectedIds.value, getSelectedInteractions())
}

function clearSelection() {
  selectedIds.value = []
  emit('selection-change', [], [])
}

function getSelectedInteractions() {
  return props.interactions.filter(i => selectedIds.value.includes(i.interaction_id))
}

function analyzeSelected() {
  emit('analyze-selected', selectedIds.value, getSelectedInteractions())
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

function handleRowClick(event, interaction) {
  // Don't navigate if clicking on checkbox
  if (event.target.type === 'checkbox') return
  emit('row-click', interaction)
  router.push(`/interactions/${interaction.interaction_id}`)
}
</script>

<style scoped>
.checkbox-col {
  width: 40px;
  text-align: center;
}

.checkbox-col input[type="checkbox"] {
  width: 16px;
  height: 16px;
  cursor: pointer;
  accent-color: var(--td-green);
}

.selected-row {
  background-color: var(--td-green-light) !important;
}

.selected-row:hover {
  background-color: #e6f4ea !important;
}

/* Floating Action Bar */
.selection-action-bar {
  position: fixed;
  bottom: 24px;
  left: 50%;
  transform: translateX(-50%);
  background: white;
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
  padding: 12px 20px;
  display: flex;
  align-items: center;
  gap: 24px;
  z-index: 1000;
  border: 1px solid var(--td-gray-200);
}

.selection-info {
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--td-gray-700);
  font-size: 14px;
}

.selection-count {
  background: var(--td-green);
  color: white;
  font-weight: 600;
  padding: 4px 10px;
  border-radius: 16px;
  font-size: 13px;
}

.selection-actions {
  display: flex;
  gap: 8px;
}

/* Transition */
.slide-up-enter-active,
.slide-up-leave-active {
  transition: all 0.3s ease;
}

.slide-up-enter-from,
.slide-up-leave-to {
  opacity: 0;
  transform: translateX(-50%) translateY(20px);
}
</style>
