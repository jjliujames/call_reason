<template>
  <div class="severity-pyramid">
    <div class="pyramid-visual">
      <div class="pyramid-level high" :style="{ width: '40%' }">
        <span class="level-count">{{ high }}</span>
      </div>
      <div class="pyramid-level medium" :style="{ width: '65%' }">
        <span class="level-count">{{ medium }}</span>
      </div>
      <div class="pyramid-level low" :style="{ width: '90%' }">
        <span class="level-count">{{ low }}</span>
      </div>
    </div>

    <div class="pyramid-labels">
      <div class="label-row high">
        <span class="severity-dot high"></span>
        <span class="label-text">High</span>
        <span class="label-value">{{ high }}</span>
        <span class="label-percent">({{ highPercent }}%)</span>
      </div>
      <div class="label-row medium">
        <span class="severity-dot medium"></span>
        <span class="label-text">Medium</span>
        <span class="label-value">{{ medium }}</span>
        <span class="label-percent">({{ mediumPercent }}%)</span>
      </div>
      <div class="label-row low">
        <span class="severity-dot low"></span>
        <span class="label-text">Low</span>
        <span class="label-value">{{ low }}</span>
        <span class="label-percent">({{ lowPercent }}%)</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  high: { type: Number, default: 0 },
  medium: { type: Number, default: 0 },
  low: { type: Number, default: 0 }
})

const total = computed(() => props.high + props.medium + props.low)

const highPercent = computed(() =>
  total.value > 0 ? Math.round(props.high / total.value * 100) : 0
)

const mediumPercent = computed(() =>
  total.value > 0 ? Math.round(props.medium / total.value * 100) : 0
)

const lowPercent = computed(() =>
  total.value > 0 ? Math.round(props.low / total.value * 100) : 0
)
</script>

<style scoped>
.severity-pyramid {
  display: flex;
  gap: 24px;
  align-items: center;
}

.pyramid-visual {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  flex: 1;
}

.pyramid-level {
  height: 32px;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  color: white;
  font-size: 14px;
  transition: all 0.3s ease;
}

.pyramid-level:hover {
  transform: scale(1.02);
}

.pyramid-level.high {
  background: linear-gradient(135deg, #DC2626 0%, #EF4444 100%);
}

.pyramid-level.medium {
  background: linear-gradient(135deg, #D97706 0%, #F59E0B 100%);
}

.pyramid-level.low {
  background: linear-gradient(135deg, #059669 0%, #10B981 100%);
}

.level-count {
  text-shadow: 0 1px 2px rgba(0,0,0,0.2);
}

.pyramid-labels {
  display: flex;
  flex-direction: column;
  gap: 8px;
  min-width: 160px;
}

.label-row {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
}

.severity-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
}

.severity-dot.high {
  background: #DC2626;
}

.severity-dot.medium {
  background: #D97706;
}

.severity-dot.low {
  background: #059669;
}

.label-text {
  font-weight: 500;
  color: var(--td-gray-700);
  min-width: 55px;
}

.label-value {
  font-weight: 600;
  color: var(--td-gray-900);
}

.label-percent {
  color: var(--td-gray-500);
  font-size: 12px;
}
</style>
