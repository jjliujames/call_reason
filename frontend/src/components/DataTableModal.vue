<template>
  <div v-if="show" class="modal-overlay" @click.self="close">
    <div class="modal-content">
      <div class="modal-header">
        <h3 class="modal-title">{{ title }}</h3>
        <button class="modal-close" @click="close">&times;</button>
      </div>

      <div class="modal-body">
        <table class="data-export-table">
          <thead>
            <tr>
              <th>{{ rowLabel }}</th>
              <th v-for="label in labels" :key="label">{{ formatLabel(label) }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(row, index) in rows" :key="index">
              <td class="row-name">{{ row.name }}</td>
              <td v-for="(value, colIndex) in row.values" :key="colIndex">
                {{ formatValue(value) }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div class="modal-footer">
        <button class="btn btn-secondary" @click="copyToClipboard">
          <span v-if="copied">Copied!</span>
          <span v-else>Copy to Clipboard</span>
        </button>
        <button class="btn btn-primary" @click="downloadCsv">
          Download CSV
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  show: { type: Boolean, default: false },
  title: { type: String, default: 'Data Table' },
  labels: { type: Array, required: true }, // Column headers (e.g., week labels)
  rows: { type: Array, required: true }, // { name: string, values: number[] }
  rowLabel: { type: String, default: 'Metric' },
  valueFormat: { type: String, default: 'number' } // number, percent, currency
})

const emit = defineEmits(['close'])

const copied = ref(false)

function close() {
  emit('close')
}

function formatLabel(label) {
  // Remove year prefix from week labels like "2024-W01" -> "W01"
  if (label.match(/^\d{4}-W\d{2}$/)) {
    return label.replace(/^\d{4}-/, '')
  }
  return label
}

function formatValue(value) {
  if (value === null || value === undefined) return '—'
  if (props.valueFormat === 'percent') return `${value}%`
  if (props.valueFormat === 'currency') return `$${value.toLocaleString()}`
  return value.toLocaleString()
}

function generateCsvContent() {
  const headerRow = [props.rowLabel, ...props.labels.map(formatLabel)].join(',')
  const dataRows = props.rows.map(row => {
    return [row.name, ...row.values].join(',')
  })
  return [headerRow, ...dataRows].join('\n')
}

async function copyToClipboard() {
  const content = generateCsvContent()
  try {
    await navigator.clipboard.writeText(content)
    copied.value = true
    setTimeout(() => {
      copied.value = false
    }, 2000)
  } catch (err) {
    console.error('Failed to copy:', err)
  }
}

function downloadCsv() {
  const content = generateCsvContent()
  const blob = new Blob([content], { type: 'text/csv;charset=utf-8;' })
  const link = document.createElement('a')
  const url = URL.createObjectURL(blob)

  link.setAttribute('href', url)
  link.setAttribute('download', `${props.title.replace(/\s+/g, '_')}.csv`)
  link.style.visibility = 'hidden'
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 12px;
  width: 90%;
  max-width: 800px;
  max-height: 80vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.2);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid var(--td-gray-200);
}

.modal-title {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: var(--td-gray-900);
}

.modal-close {
  background: none;
  border: none;
  font-size: 24px;
  color: var(--td-gray-500);
  cursor: pointer;
  padding: 0;
  line-height: 1;
}

.modal-close:hover {
  color: var(--td-gray-900);
}

.modal-body {
  flex: 1;
  overflow: auto;
  padding: 20px;
}

.data-export-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
}

.data-export-table th,
.data-export-table td {
  padding: 10px 12px;
  text-align: right;
  border-bottom: 1px solid var(--td-gray-200);
}

.data-export-table th {
  background: var(--td-gray-50);
  font-weight: 600;
  color: var(--td-gray-700);
  position: sticky;
  top: 0;
}

.data-export-table th:first-child,
.data-export-table td:first-child {
  text-align: left;
}

.data-export-table .row-name {
  font-weight: 500;
  color: var(--td-gray-900);
}

.data-export-table tbody tr:hover {
  background: var(--td-gray-50);
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 16px 20px;
  border-top: 1px solid var(--td-gray-200);
}

.btn {
  padding: 8px 16px;
  border-radius: 6px;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-secondary {
  background: white;
  border: 1px solid var(--td-gray-300);
  color: var(--td-gray-700);
}

.btn-secondary:hover {
  background: var(--td-gray-50);
}

.btn-primary {
  background: var(--td-green);
  border: 1px solid var(--td-green);
  color: white;
}

.btn-primary:hover {
  background: var(--td-green-dark);
}
</style>
