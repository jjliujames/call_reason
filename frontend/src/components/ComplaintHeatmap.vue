<template>
  <div class="complaint-heatmap">
    <div class="heatmap-scroll">
      <table class="heatmap-table">
        <thead>
          <tr>
            <th class="product-header">Product</th>
            <th
              v-for="category in categories"
              :key="category"
              class="category-header"
              :title="category"
            >
              {{ truncate(category, 12) }}
            </th>
            <th class="total-header">Total</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="row in data" :key="row.product">
            <td class="product-cell">{{ truncate(row.product, 20) }}</td>
            <td
              v-for="category in categories"
              :key="category"
              class="heat-cell"
              :style="getCellStyle(row.categories[category] || 0)"
              :title="`${row.product}: ${category} - ${row.categories[category] || 0}`"
              @click="$emit('cell-click', { product: row.product, category, count: row.categories[category] || 0 })"
            >
              {{ row.categories[category] || '' }}
            </td>
            <td class="total-cell">{{ row.total }}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <div class="heatmap-legend">
      <span class="legend-label">Low</span>
      <div class="legend-gradient"></div>
      <span class="legend-label">High</span>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  data: { type: Array, default: () => [] },
  categories: { type: Array, default: () => [] },
  maxValue: { type: Number, default: null }
})

defineEmits(['cell-click'])

const computedMax = computed(() => {
  if (props.maxValue) return props.maxValue
  let max = 0
  for (const row of props.data) {
    for (const cat of props.categories) {
      const val = row.categories?.[cat] || 0
      if (val > max) max = val
    }
  }
  return max || 1
})

function getCellStyle(value) {
  if (!value) return { background: '#f8f9fa' }

  const intensity = Math.min(value / computedMax.value, 1)

  // Gradient from light green to dark red
  const r = Math.round(220 + (220 - 220) * intensity)
  const g = Math.round(252 - intensity * 200)
  const b = Math.round(231 - intensity * 180)

  // Use a color scale: green -> yellow -> orange -> red
  let bgColor
  if (intensity < 0.25) {
    bgColor = `rgba(34, 197, 94, ${0.1 + intensity * 0.4})`
  } else if (intensity < 0.5) {
    bgColor = `rgba(234, 179, 8, ${0.2 + intensity * 0.4})`
  } else if (intensity < 0.75) {
    bgColor = `rgba(249, 115, 22, ${0.3 + intensity * 0.4})`
  } else {
    bgColor = `rgba(239, 68, 68, ${0.4 + intensity * 0.4})`
  }

  return {
    background: bgColor,
    color: intensity > 0.6 ? 'white' : 'inherit',
    fontWeight: intensity > 0.5 ? '600' : '400'
  }
}

function truncate(str, len) {
  if (!str) return ''
  return str.length > len ? str.substring(0, len) + '...' : str
}
</script>

<style scoped>
.complaint-heatmap {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.heatmap-scroll {
  overflow-x: auto;
}

.heatmap-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 12px;
}

.heatmap-table th,
.heatmap-table td {
  padding: 8px 6px;
  text-align: center;
  border: 1px solid var(--td-gray-200);
}

.product-header,
.product-cell {
  text-align: left;
  font-weight: 500;
  background: var(--td-gray-50);
  white-space: nowrap;
  position: sticky;
  left: 0;
  z-index: 1;
}

.product-cell {
  font-weight: 400;
  max-width: 150px;
  overflow: hidden;
  text-overflow: ellipsis;
}

.category-header {
  font-size: 11px;
  font-weight: 600;
  color: var(--td-gray-700);
  white-space: nowrap;
  min-width: 70px;
}

.total-header,
.total-cell {
  font-weight: 600;
  background: var(--td-gray-100);
}

.heat-cell {
  cursor: pointer;
  transition: all 0.2s ease;
  min-width: 50px;
}

.heat-cell:hover {
  transform: scale(1.1);
  box-shadow: 0 2px 8px rgba(0,0,0,0.15);
  z-index: 2;
  position: relative;
}

.heatmap-legend {
  display: flex;
  align-items: center;
  gap: 8px;
  justify-content: flex-end;
}

.legend-label {
  font-size: 11px;
  color: var(--td-gray-600);
}

.legend-gradient {
  width: 100px;
  height: 12px;
  border-radius: 4px;
  background: linear-gradient(to right,
    rgba(34, 197, 94, 0.3),
    rgba(234, 179, 8, 0.5),
    rgba(249, 115, 22, 0.6),
    rgba(239, 68, 68, 0.8)
  );
}
</style>
