<template>
  <div :class="['kpi-card-enhanced', variant, { clickable: clickable }]" @click="handleClick">
    <div class="kpi-main">
      <div class="kpi-header">
        <span class="kpi-label">{{ label }}</span>
        <span v-if="tooltip" class="kpi-tooltip" :title="tooltip">?</span>
      </div>

      <div class="kpi-body">
        <div class="kpi-value-row">
          <span class="kpi-value">{{ formattedValue }}</span>
          <span v-if="suffix" class="kpi-suffix">{{ suffix }}</span>
        </div>

        <div v-if="showTrend && delta !== null" class="kpi-trend" :class="trendClass">
          <span class="trend-arrow">{{ trendArrow }}</span>
          <span class="trend-value">{{ formattedDelta }}</span>
          <span v-if="deltaLabel" class="trend-label">{{ deltaLabel }}</span>
        </div>
      </div>

      <div v-if="subtext" class="kpi-subtext">{{ subtext }}</div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  label: { type: String, required: true },
  value: { type: [Number, String], required: true },
  format: { type: String, default: 'number' }, // number, currency, percent, time
  suffix: { type: String, default: '' },
  delta: { type: Number, default: null },
  deltaPercent: { type: Number, default: null },
  deltaLabel: { type: String, default: 'WoW' },
  isPositiveGood: { type: Boolean, default: true }, // For determining trend color
  variant: { type: String, default: 'default' }, // default, highlight, warning, danger, success
  showTrend: { type: Boolean, default: true },
  tooltip: { type: String, default: '' },
  subtext: { type: String, default: '' },
  clickable: { type: Boolean, default: false }
})

const emit = defineEmits(['click'])

const formattedValue = computed(() => {
  if (props.value === null || props.value === undefined) return '—'

  switch (props.format) {
    case 'currency':
      return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(props.value)
    case 'percent':
      return `${props.value}%`
    case 'time':
      return `${props.value} min`
    case 'decimal':
      return props.value.toLocaleString(undefined, { minimumFractionDigits: 1, maximumFractionDigits: 1 })
    default:
      return typeof props.value === 'number' ? props.value.toLocaleString() : props.value
  }
})

const formattedDelta = computed(() => {
  if (props.deltaPercent !== null) {
    return `${Math.abs(props.deltaPercent)}%`
  }
  if (props.delta !== null) {
    const absVal = Math.abs(props.delta)
    if (props.format === 'percent') return `${absVal}pp`
    if (props.format === 'currency') return `$${absVal.toLocaleString()}`
    if (props.format === 'time') return `${absVal} min`
    return absVal.toLocaleString()
  }
  return ''
})

const trendDirection = computed(() => {
  const d = props.deltaPercent ?? props.delta ?? 0
  if (d > 0) return 'up'
  if (d < 0) return 'down'
  return 'flat'
})

const trendArrow = computed(() => {
  if (trendDirection.value === 'up') return '▲'
  if (trendDirection.value === 'down') return '▼'
  return '—'
})

const trendClass = computed(() => {
  if (trendDirection.value === 'flat') return 'neutral'
  const isGood = props.isPositiveGood
    ? trendDirection.value === 'up'
    : trendDirection.value === 'down'
  return isGood ? 'positive' : 'negative'
})

function handleClick() {
  if (props.clickable) {
    emit('click')
  }
}
</script>

<style scoped>
.kpi-card-enhanced {
  background: white;
  border-radius: 8px;
  border-left: 4px solid var(--td-green);
  box-shadow: 0 1px 3px rgba(0,0,0,0.08);
  transition: all 0.2s ease;
  overflow: hidden;
}

.kpi-main {
  padding: 16px;
}

.kpi-card-enhanced.clickable {
  cursor: pointer;
}

.kpi-card-enhanced.clickable:hover {
  box-shadow: 0 4px 12px rgba(0,0,0,0.12);
  transform: translateY(-2px);
}

.kpi-card-enhanced.highlight {
  border-left-color: var(--td-green);
  background: linear-gradient(135deg, #f0fdf4 0%, white 100%);
}

.kpi-card-enhanced.warning {
  border-left-color: var(--td-orange);
}

.kpi-card-enhanced.danger {
  border-left-color: var(--td-red);
}

.kpi-card-enhanced.success {
  border-left-color: #10B981;
}

.kpi-header {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 8px;
}

.kpi-label {
  font-size: 11px;
  font-weight: 500;
  color: var(--td-gray-600);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  flex: 1;
}

.kpi-tooltip {
  width: 14px;
  height: 14px;
  border-radius: 50%;
  background: var(--td-gray-300);
  color: var(--td-gray-600);
  font-size: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: help;
}

.kpi-body {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.kpi-value-row {
  display: flex;
  align-items: baseline;
  gap: 4px;
}

.kpi-value {
  font-size: 22px;
  font-weight: 700;
  color: var(--td-gray-900);
  line-height: 1.2;
}

.kpi-suffix {
  font-size: 14px;
  font-weight: 500;
  color: var(--td-gray-500);
}

.kpi-trend {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  font-weight: 500;
}

.kpi-trend.positive {
  color: #10B981;
}

.kpi-trend.negative {
  color: var(--td-red);
}

.kpi-trend.neutral {
  color: var(--td-gray-500);
}

.trend-arrow {
  font-size: 10px;
}

.trend-label {
  font-size: 11px;
  color: var(--td-gray-500);
  margin-left: 2px;
}

.kpi-subtext {
  font-size: 11px;
  color: var(--td-gray-500);
  margin-top: 8px;
}
</style>
