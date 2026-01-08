<template>
  <div class="ai-summary-panel" :class="{ collapsed: isCollapsed, loading: loading }">
    <div class="panel-header" @click="toggleCollapse">
      <div class="header-left">
        <span class="ai-icon">&#129302;</span>
        <h3 class="panel-title">AI Executive Brief</h3>
        <span v-if="lastGenerated" class="last-updated">
          Generated {{ lastGenerated }}
        </span>
      </div>
      <div class="header-right">
        <button
          v-if="!isCollapsed"
          class="regenerate-btn"
          @click.stop="generateSummary"
          :disabled="loading"
        >
          <span v-if="loading" class="spinner"></span>
          <span v-else>&#8635;</span>
          {{ loading ? 'Generating...' : 'Regenerate' }}
        </button>
        <button class="collapse-btn" :title="isCollapsed ? 'Expand' : 'Collapse'">
          {{ isCollapsed ? '&#9660;' : '&#9650;' }}
        </button>
      </div>
    </div>

    <div v-if="!isCollapsed" class="panel-content">
      <!-- Loading State -->
      <div v-if="loading" class="loading-state">
        <div class="skeleton skeleton-line wide"></div>
        <div class="skeleton skeleton-line medium"></div>
        <div class="skeleton skeleton-line narrow"></div>
        <div class="skeleton-section">
          <div class="skeleton skeleton-line medium"></div>
          <div class="skeleton skeleton-line narrow"></div>
        </div>
      </div>

      <!-- Empty State -->
      <div v-else-if="!summaryData" class="empty-state">
        <p>Click "Generate AI Brief" to analyze current data and get executive insights.</p>
        <button class="generate-btn" @click="generateSummary">
          Generate AI Brief
        </button>
      </div>

      <!-- Summary Content -->
      <div v-else class="summary-content">
        <!-- Key Finding -->
        <div class="key-finding">
          <span class="finding-label">Key Finding:</span>
          <span class="finding-text">{{ summaryData.key_finding }}</span>
        </div>

        <!-- Anomalies -->
        <div v-if="summaryData.anomalies?.length" class="anomalies-section">
          <div
            v-for="(anomaly, index) in summaryData.anomalies"
            :key="index"
            :class="['anomaly-badge', anomaly.severity]"
          >
            <span class="anomaly-icon">{{ anomaly.severity === 'high' ? '&#9888;' : '&#9432;' }}</span>
            {{ anomaly.message }}
          </div>
        </div>

        <!-- Details -->
        <div v-if="summaryData.details?.length" class="details-section">
          <p v-for="(detail, index) in summaryData.details" :key="index" class="detail-text">
            {{ detail }}
          </p>
        </div>

        <!-- Actions -->
        <div v-if="summaryData.actions?.length" class="actions-section">
          <h4 class="section-title">Recommended Priority Actions:</h4>
          <div class="actions-list">
            <div
              v-for="(action, index) in summaryData.actions.slice(0, 3)"
              :key="index"
              class="action-item"
            >
              <span class="action-number">{{ index + 1 }}</span>
              <div class="action-content">
                <span class="action-text">{{ action.text }}</span>
                <div class="action-meta">
                  <span :class="['impact-badge', action.impact?.toLowerCase()]">
                    {{ action.impact }} Impact
                  </span>
                  <span v-if="action.estimated_impact" class="estimated-impact">
                    Est: {{ action.estimated_impact }}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Positive Trends -->
        <div v-if="summaryData.positive_trends?.length" class="positive-section">
          <h4 class="section-title positive">Positive Developments:</h4>
          <ul class="positive-list">
            <li v-for="(trend, index) in summaryData.positive_trends" :key="index">
              {{ trend }}
            </li>
          </ul>
        </div>

        <!-- Confidence -->
        <div class="confidence-row">
          <span class="confidence-label">Analysis Confidence:</span>
          <div class="confidence-bar">
            <div
              class="confidence-fill"
              :style="{ width: (summaryData.confidence * 100) + '%' }"
            ></div>
          </div>
          <span class="confidence-value">{{ Math.round(summaryData.confidence * 100) }}%</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import { getAISummary } from '../services/api'

const props = defineProps({
  filters: {
    type: Object,
    default: () => ({})
  },
  autoGenerate: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['generated'])

const isCollapsed = ref(true)
const loading = ref(false)
const summaryData = ref(null)
const lastGenerated = ref(null)
const error = ref(null)

async function generateSummary() {
  loading.value = true
  error.value = null

  try {
    const response = await getAISummary(props.filters)

    if (response.success) {
      summaryData.value = response.summary
      lastGenerated.value = new Date().toLocaleTimeString()
      emit('generated', response)
    } else {
      error.value = 'Failed to generate summary'
    }
  } catch (err) {
    console.error('AI Summary error:', err)
    error.value = err.message || 'Failed to generate summary'
  } finally {
    loading.value = false
  }
}

function toggleCollapse() {
  isCollapsed.value = !isCollapsed.value
}

// Auto-generate on mount if prop is set
onMounted(() => {
  if (props.autoGenerate) {
    generateSummary()
  }
})

// Optionally regenerate when filters change significantly
watch(() => props.filters, (newFilters, oldFilters) => {
  // Only auto-regenerate if we already have data and filters changed meaningfully
  if (summaryData.value && JSON.stringify(newFilters) !== JSON.stringify(oldFilters)) {
    // Clear existing data to show stale state
    // User can click regenerate to get new analysis
    lastGenerated.value = lastGenerated.value + ' (filters changed)'
  }
}, { deep: true })

// Expose method for parent to trigger generation
defineExpose({ generateSummary })
</script>

<style scoped>
.ai-summary-panel {
  background: linear-gradient(135deg, #f8fafc 0%, #f0f9ff 100%);
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  margin-bottom: 24px;
  overflow: hidden;
  transition: all 0.3s ease;
}

.ai-summary-panel.loading {
  background: linear-gradient(135deg, #f8fafc 0%, #fefce8 100%);
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  background: rgba(255, 255, 255, 0.7);
  border-bottom: 1px solid #e2e8f0;
  cursor: pointer;
}

.ai-summary-panel.collapsed .panel-header {
  border-bottom: none;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.ai-icon {
  font-size: 20px;
}

.panel-title {
  margin: 0;
  font-size: 15px;
  font-weight: 600;
  color: #1e293b;
}

.last-updated {
  font-size: 11px;
  color: #64748b;
  background: #e2e8f0;
  padding: 2px 8px;
  border-radius: 10px;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.regenerate-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  background: var(--td-green);
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.2s;
}

.regenerate-btn:hover:not(:disabled) {
  background: #006b31;
}

.regenerate-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.spinner {
  display: inline-block;
  width: 12px;
  height: 12px;
  border: 2px solid rgba(255,255,255,0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.collapse-btn {
  background: transparent;
  border: none;
  font-size: 12px;
  color: #64748b;
  cursor: pointer;
  padding: 4px 8px;
}

.panel-content {
  padding: 20px;
}

/* Loading State */
.loading-state {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.skeleton {
  background: linear-gradient(90deg, #e2e8f0 25%, #f1f5f9 50%, #e2e8f0 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  border-radius: 4px;
}

.skeleton-line {
  height: 14px;
}

.skeleton-line.wide { width: 90%; }
.skeleton-line.medium { width: 70%; }
.skeleton-line.narrow { width: 50%; }

.skeleton-section {
  margin-top: 16px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

@keyframes shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

/* Empty State */
.empty-state {
  text-align: center;
  padding: 24px;
  color: #64748b;
}

.empty-state p {
  margin-bottom: 16px;
}

.generate-btn {
  padding: 10px 24px;
  background: var(--td-green);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.2s;
}

.generate-btn:hover {
  background: #006b31;
}

/* Summary Content */
.summary-content {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.key-finding {
  background: white;
  padding: 16px;
  border-radius: 8px;
  border-left: 4px solid var(--td-green);
}

.finding-label {
  display: block;
  font-size: 11px;
  font-weight: 600;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 6px;
}

.finding-text {
  font-size: 15px;
  font-weight: 500;
  color: #1e293b;
  line-height: 1.5;
}

/* Anomalies */
.anomalies-section {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.anomaly-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 500;
}

.anomaly-badge.high {
  background: #fef2f2;
  color: #dc2626;
  border: 1px solid #fecaca;
}

.anomaly-badge.medium {
  background: #fefce8;
  color: #ca8a04;
  border: 1px solid #fef08a;
}

.anomaly-icon {
  font-size: 14px;
}

/* Details */
.details-section {
  padding: 0 4px;
}

.detail-text {
  margin: 0 0 8px 0;
  font-size: 13px;
  color: #475569;
  line-height: 1.6;
}

.detail-text:last-child {
  margin-bottom: 0;
}

/* Actions */
.actions-section {
  background: white;
  padding: 16px;
  border-radius: 8px;
}

.section-title {
  margin: 0 0 12px 0;
  font-size: 13px;
  font-weight: 600;
  color: #1e293b;
}

.section-title.positive {
  color: #059669;
}

.actions-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.action-item {
  display: flex;
  gap: 12px;
  align-items: flex-start;
}

.action-number {
  width: 24px;
  height: 24px;
  background: var(--td-green);
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 600;
  flex-shrink: 0;
}

.action-content {
  flex: 1;
}

.action-text {
  display: block;
  font-size: 13px;
  color: #334155;
  line-height: 1.4;
  margin-bottom: 6px;
}

.action-meta {
  display: flex;
  align-items: center;
  gap: 12px;
}

.impact-badge {
  font-size: 10px;
  font-weight: 600;
  padding: 2px 8px;
  border-radius: 10px;
  text-transform: uppercase;
}

.impact-badge.high {
  background: #dcfce7;
  color: #166534;
}

.impact-badge.medium {
  background: #fef9c3;
  color: #854d0e;
}

.impact-badge.low {
  background: #f1f5f9;
  color: #475569;
}

.estimated-impact {
  font-size: 11px;
  color: #64748b;
  font-style: italic;
}

/* Positive Section */
.positive-section {
  background: #f0fdf4;
  padding: 12px 16px;
  border-radius: 8px;
}

.positive-list {
  margin: 0;
  padding-left: 20px;
}

.positive-list li {
  font-size: 13px;
  color: #166534;
  margin-bottom: 4px;
}

.positive-list li:last-child {
  margin-bottom: 0;
}

/* Confidence */
.confidence-row {
  display: flex;
  align-items: center;
  gap: 12px;
  padding-top: 12px;
  border-top: 1px solid #e2e8f0;
}

.confidence-label {
  font-size: 11px;
  color: #64748b;
}

.confidence-bar {
  flex: 1;
  height: 6px;
  background: #e2e8f0;
  border-radius: 3px;
  overflow: hidden;
  max-width: 120px;
}

.confidence-fill {
  height: 100%;
  background: var(--td-green);
  transition: width 0.3s ease;
}

.confidence-value {
  font-size: 11px;
  font-weight: 600;
  color: #475569;
}

/* Responsive */
@media (max-width: 768px) {
  .panel-header {
    flex-direction: column;
    gap: 12px;
    align-items: flex-start;
  }

  .header-right {
    width: 100%;
    justify-content: space-between;
  }

  .action-item {
    flex-direction: column;
    gap: 8px;
  }

  .action-number {
    width: 20px;
    height: 20px;
    font-size: 11px;
  }
}
</style>
