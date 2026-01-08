<template>
  <div :class="['kpi-card-enhanced', variant, { clickable: clickable || expandable, expanded }]">
    <div class="kpi-main" @click="handleClick">
      <div class="kpi-header">
        <span class="kpi-label">{{ label }}</span>
        <span v-if="tooltip" class="kpi-tooltip" :title="tooltip">?</span>
        <span v-if="expandable" class="kpi-expand-icon" :class="{ rotated: expanded }">
          <svg width="12" height="12" viewBox="0 0 12 12" fill="none">
            <path d="M3 4.5L6 7.5L9 4.5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </span>
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

      <div v-if="sparklineData && sparklineData.length > 0 && !expanded" class="kpi-sparkline">
        <apexchart
          type="area"
          height="40"
          :options="sparklineOptions"
          :series="sparklineSeries"
        />
      </div>

      <div v-if="subtext" class="kpi-subtext">{{ subtext }}</div>
    </div>

    <!-- Expanded Weekly Trend Panel -->
    <Transition name="expand">
      <div v-if="expanded && weeklyTrendData" class="kpi-expanded-panel">
        <div class="expanded-header">
          <span class="expanded-title">Weekly Trend</span>
          <span v-if="weeklyTrendData.wow_change !== null" class="expanded-wow" :class="getWowClass(weeklyTrendData.wow_change)">
            {{ weeklyTrendData.wow_change > 0 ? '+' : '' }}{{ weeklyTrendData.wow_change }}% WoW
          </span>
        </div>
        <apexchart
          type="bar"
          height="120"
          :options="weeklyChartOptions"
          :series="weeklyChartSeries"
        />
        <div class="expanded-footer">
          <div class="week-stat">
            <span class="week-label">Current Week</span>
            <span class="week-value">{{ formatWeekValue(weeklyTrendData.current_value) }}</span>
          </div>
          <div class="week-stat">
            <span class="week-label">Previous Week</span>
            <span class="week-value">{{ formatWeekValue(weeklyTrendData.previous_value) }}</span>
          </div>
        </div>
      </div>
    </Transition>

    <!-- Loading state for expanded panel -->
    <div v-if="expanded && loadingTrend" class="kpi-expanded-panel loading">
      <div class="loading-spinner"></div>
      <span>Loading trends...</span>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'

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
  sparklineData: { type: Array, default: () => [] },
  sparklineColor: { type: String, default: '#00843D' },
  tooltip: { type: String, default: '' },
  subtext: { type: String, default: '' },
  clickable: { type: Boolean, default: false },
  expandable: { type: Boolean, default: false },
  metricKey: { type: String, default: '' }, // Key for fetching weekly trends
  weeklyTrendData: { type: Object, default: null },
  loadingTrend: { type: Boolean, default: false }
})

const emit = defineEmits(['click', 'expand', 'collapse'])

const expanded = ref(false)

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

const sparklineOptions = computed(() => ({
  chart: {
    type: 'area',
    sparkline: { enabled: true },
    toolbar: { show: false },
    animations: { enabled: false }
  },
  stroke: { curve: 'smooth', width: 2 },
  fill: {
    type: 'gradient',
    gradient: {
      shadeIntensity: 1,
      opacityFrom: 0.4,
      opacityTo: 0.1,
      stops: [0, 100]
    }
  },
  colors: [props.sparklineColor],
  tooltip: { enabled: false }
}))

const sparklineSeries = computed(() => [{
  name: props.label,
  data: props.sparklineData
}])

// Weekly chart options
const weeklyChartOptions = computed(() => ({
  chart: {
    type: 'bar',
    toolbar: { show: false },
    animations: { enabled: false }
  },
  plotOptions: {
    bar: {
      borderRadius: 4,
      columnWidth: '60%'
    }
  },
  colors: [props.sparklineColor || '#00843D'],
  dataLabels: { enabled: false },
  xaxis: {
    categories: props.weeklyTrendData?.labels?.map(l => l.replace(/^\d{4}-/, '')) || [],
    labels: {
      style: { fontSize: '10px', colors: '#6B7280' }
    }
  },
  yaxis: {
    labels: {
      style: { fontSize: '10px', colors: '#6B7280' },
      formatter: (val) => {
        if (props.format === 'percent') return `${val}%`
        if (props.format === 'time') return `${val}m`
        return val >= 1000 ? `${(val / 1000).toFixed(1)}k` : val
      }
    }
  },
  grid: {
    borderColor: '#E5E7EB',
    strokeDashArray: 3
  },
  tooltip: {
    y: {
      formatter: (val) => formatWeekValue(val)
    }
  }
}))

const weeklyChartSeries = computed(() => [{
  name: props.label,
  data: props.weeklyTrendData?.values || []
}])

function formatWeekValue(val) {
  if (val === null || val === undefined) return '—'
  switch (props.format) {
    case 'percent':
      return `${val}%`
    case 'time':
      return `${val} min`
    case 'currency':
      return `$${val.toLocaleString()}`
    default:
      return val.toLocaleString()
  }
}

function getWowClass(change) {
  if (change === null) return 'neutral'
  const isUp = change > 0
  const isGood = props.isPositiveGood ? isUp : !isUp
  return isGood ? 'positive' : 'negative'
}

function handleClick() {
  if (props.expandable) {
    expanded.value = !expanded.value
    emit(expanded.value ? 'expand' : 'collapse', props.metricKey)
  } else if (props.clickable) {
    emit('click')
  }
}

// Close expanded state when another card expands
watch(() => props.weeklyTrendData, (newData) => {
  if (newData === null && expanded.value) {
    // Data was cleared, might need to re-fetch
  }
})
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
}

.kpi-card-enhanced.expanded {
  box-shadow: 0 4px 16px rgba(0,0,0,0.15);
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
  font-size: 12px;
  font-weight: 500;
  color: var(--td-gray-600);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  flex: 1;
}

.kpi-expand-icon {
  color: var(--td-gray-400);
  transition: transform 0.2s ease;
}

.kpi-expand-icon.rotated {
  transform: rotate(180deg);
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
  font-size: 24px;
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

.kpi-sparkline {
  margin-top: 8px;
  margin-bottom: -8px;
  margin-left: -8px;
  margin-right: -8px;
}

.kpi-subtext {
  font-size: 11px;
  color: var(--td-gray-500);
  margin-top: 8px;
}

/* Expanded Panel */
.kpi-expanded-panel {
  padding: 12px 16px 16px;
  background: var(--td-gray-50);
  border-top: 1px solid var(--td-gray-200);
}

.kpi-expanded-panel.loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 24px;
  color: var(--td-gray-500);
  font-size: 13px;
}

.loading-spinner {
  width: 24px;
  height: 24px;
  border: 2px solid var(--td-gray-200);
  border-top-color: var(--td-green);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.expanded-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.expanded-title {
  font-size: 12px;
  font-weight: 600;
  color: var(--td-gray-700);
}

.expanded-wow {
  font-size: 12px;
  font-weight: 600;
  padding: 2px 8px;
  border-radius: 12px;
}

.expanded-wow.positive {
  background: #D1FAE5;
  color: #047857;
}

.expanded-wow.negative {
  background: #FEE2E2;
  color: #B91C1C;
}

.expanded-wow.neutral {
  background: var(--td-gray-200);
  color: var(--td-gray-600);
}

.expanded-footer {
  display: flex;
  gap: 16px;
  margin-top: 8px;
  padding-top: 8px;
  border-top: 1px dashed var(--td-gray-200);
}

.week-stat {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.week-label {
  font-size: 10px;
  color: var(--td-gray-500);
  text-transform: uppercase;
}

.week-value {
  font-size: 14px;
  font-weight: 600;
  color: var(--td-gray-800);
}

/* Expand Transition */
.expand-enter-active,
.expand-leave-active {
  transition: all 0.3s ease;
  max-height: 300px;
}

.expand-enter-from,
.expand-leave-to {
  opacity: 0;
  max-height: 0;
  padding-top: 0;
  padding-bottom: 0;
}
</style>
