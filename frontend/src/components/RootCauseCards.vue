<template>
  <div class="root-cause-results">
    <div v-if="loading" class="loading">Analyzing root causes...</div>

    <template v-else-if="result">
      <!-- Executive Summary -->
      <div class="card" style="margin-bottom: 20px; border-left: 4px solid var(--td-green);">
        <div class="card-header">
          <span class="card-title">Executive Summary</span>
        </div>
        <div class="card-body">
          <p style="font-size: 14px; line-height: 1.7;" v-html="formatSummary(result.executive_summary)"></p>
          <p style="margin-top: 12px; font-size: 13px; color: var(--td-gray-600);">
            Analyzed {{ result.total_analyzed }} interactions ({{ result.total_complaints }} complaints)
          </p>
        </div>
      </div>

      <!-- Root Cause Cards -->
      <div v-for="(cause, index) in result.root_causes" :key="cause.root_cause_label" class="root-cause-card">
        <div class="root-cause-header">
          <div>
            <span style="font-size: 13px; color: var(--td-gray-500); margin-right: 8px;">#{{ index + 1 }}</span>
            <span class="root-cause-title">{{ cause.root_cause_label }}</span>
          </div>
          <div style="display: flex; gap: 8px; align-items: center;">
            <span class="badge badge-yellow">Impact: {{ cause.impact_score }}</span>
            <span :class="['concentration-badge', cause.concentration === 'Systemic' ? 'systemic' : 'concentrated']">
              {{ cause.concentration }}
            </span>
            <button
              class="export-btn"
              @click="openExportModal(cause)"
              title="Export data table"
            >
              Export
            </button>
          </div>
        </div>

        <p style="font-size: 13px; color: var(--td-gray-600); margin-bottom: 16px;">
          {{ cause.description }}
        </p>

        <!-- Weekly Trend Chart -->
        <div class="trend-section" v-if="trendData[cause.root_cause_label]">
          <div class="trend-header">
            <span class="trend-title">Weekly Trend</span>
            <span v-if="trendData[cause.root_cause_label].wow_change !== null" :class="['wow-badge', getWowClass(trendData[cause.root_cause_label].wow_change)]">
              {{ trendData[cause.root_cause_label].wow_change > 0 ? '+' : '' }}{{ trendData[cause.root_cause_label].wow_change }}% WoW
            </span>
          </div>
          <apexchart
            type="bar"
            height="120"
            :options="getTrendChartOptions(cause.root_cause_label)"
            :series="getTrendChartSeries(cause.root_cause_label)"
          />
        </div>
        <div v-else-if="loadingTrends[cause.root_cause_label]" class="trend-loading">
          Loading trend...
        </div>

        <div class="root-cause-metrics">
          <div class="root-cause-metric">
            <div class="root-cause-metric-value">{{ cause.frequency }}</div>
            <div class="root-cause-metric-label">Complaints ({{ cause.percentage }}%)</div>
          </div>
          <div class="root-cause-metric">
            <div class="root-cause-metric-value">{{ cause.avg_handling_time_minutes }} min</div>
            <div class="root-cause-metric-label">Avg Handle Time</div>
          </div>
          <div class="root-cause-metric">
            <div class="root-cause-metric-value">{{ cause.fcr_rate }}%</div>
            <div class="root-cause-metric-label">FCR Rate</div>
          </div>
          <div class="root-cause-metric" v-if="cause.top_agent_share">
            <div class="root-cause-metric-value">{{ cause.top_agent_share }}%</div>
            <div class="root-cause-metric-label">Top 3 Agent Share</div>
          </div>
        </div>

        <!-- Top Agents (if concentrated) -->
        <div v-if="cause.concentration === 'Agent-Concentrated' && cause.top_agents?.length" style="margin-bottom: 16px;">
          <div style="font-size: 12px; font-weight: 600; color: var(--td-gray-600); margin-bottom: 8px; text-transform: uppercase;">
            Top Contributing Agents
          </div>
          <div style="display: flex; gap: 12px; flex-wrap: wrap;">
            <div v-for="agent in cause.top_agents" :key="agent.agent_id" class="badge badge-orange">
              {{ agent.agent_name }} ({{ agent.count }})
            </div>
          </div>
        </div>

        <!-- Example Complaints -->
        <div v-if="cause.example_complaints?.length" style="background: var(--td-gray-100); border-radius: 6px; padding: 12px; margin-bottom: 16px;">
          <div style="font-size: 12px; font-weight: 600; color: var(--td-gray-600); margin-bottom: 8px; text-transform: uppercase;">
            Example Complaints
          </div>
          <ul class="bullet-list">
            <li v-for="(example, i) in cause.example_complaints" :key="i" style="font-size: 13px; color: var(--td-gray-700);">
              "{{ example }}"
            </li>
          </ul>
        </div>

        <!-- AI Deep Analysis Section (Expandable) -->
        <div class="ai-analysis-section">
          <button
            class="ai-analysis-toggle"
            @click="toggleAIAnalysis(cause.root_cause_label)"
            :class="{ expanded: expandedAnalysis[cause.root_cause_label] }"
          >
            <span class="ai-icon">&#129302;</span>
            <span>AI Deep Analysis</span>
            <span class="toggle-arrow">{{ expandedAnalysis[cause.root_cause_label] ? '&#9650;' : '&#9660;' }}</span>
          </button>

          <div v-if="expandedAnalysis[cause.root_cause_label]" class="ai-analysis-content">
            <div v-if="loadingAIAnalysis[cause.root_cause_label]" class="ai-loading">
              <div class="ai-loading-spinner"></div>
              Generating AI analysis...
            </div>

            <template v-else-if="aiAnalysisData[cause.root_cause_label]">
              <!-- Sub-Issues Breakdown -->
              <div v-if="aiAnalysisData[cause.root_cause_label].sub_issues?.length" class="ai-sub-section">
                <h4 class="ai-sub-title">Sub-Issue Breakdown</h4>
                <div class="sub-issues-list">
                  <div
                    v-for="(sub, i) in aiAnalysisData[cause.root_cause_label].sub_issues"
                    :key="i"
                    class="sub-issue-item"
                  >
                    <div class="sub-issue-bar">
                      <div class="sub-issue-fill" :style="{ width: sub.percentage + '%' }"></div>
                    </div>
                    <div class="sub-issue-label">
                      <span class="sub-issue-name">{{ sub.name }}</span>
                      <span class="sub-issue-pct">{{ sub.percentage }}%</span>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Correlations -->
              <div v-if="aiAnalysisData[cause.root_cause_label].correlations?.length" class="ai-sub-section">
                <h4 class="ai-sub-title">Key Correlations</h4>
                <div class="correlations-list">
                  <div
                    v-for="(corr, i) in aiAnalysisData[cause.root_cause_label].correlations"
                    :key="i"
                    class="correlation-item"
                  >
                    <span class="corr-factor">{{ corr.factor }}:</span>
                    <span class="corr-value">{{ corr.value }}</span>
                    <span class="corr-insight">{{ corr.insight }}</span>
                  </div>
                </div>
              </div>

              <!-- Analysis Summary -->
              <div v-if="aiAnalysisData[cause.root_cause_label].analysis_summary" class="ai-sub-section">
                <h4 class="ai-sub-title">AI Insight</h4>
                <p class="ai-insight-text" v-html="formatAnalysisSummary(aiAnalysisData[cause.root_cause_label].analysis_summary)"></p>
              </div>

              <!-- Personalized Actions -->
              <div v-if="aiAnalysisData[cause.root_cause_label].personalized_actions?.length" class="ai-sub-section">
                <h4 class="ai-sub-title">Personalized Actions</h4>
                <div class="personalized-actions">
                  <div
                    v-for="(action, i) in aiAnalysisData[cause.root_cause_label].personalized_actions"
                    :key="i"
                    class="personalized-action"
                  >
                    <span :class="['priority-badge', action.priority?.toLowerCase()]">{{ action.priority }}</span>
                    <span class="action-text">{{ action.text }}</span>
                    <span class="action-type-tag">{{ action.type }}</span>
                  </div>
                </div>
              </div>

              <!-- Predicted Impact -->
              <div v-if="aiAnalysisData[cause.root_cause_label].predicted_impact" class="predicted-impact">
                <div class="impact-header">
                  <span class="impact-icon">&#128200;</span>
                  <span class="impact-title">Predicted Impact</span>
                </div>
                <p class="impact-message">{{ aiAnalysisData[cause.root_cause_label].predicted_impact.message }}</p>
                <div class="impact-meta">
                  <span class="impact-reduction">-{{ aiAnalysisData[cause.root_cause_label].predicted_impact.reduction_percentage }}% complaints</span>
                  <span class="impact-timeframe">{{ aiAnalysisData[cause.root_cause_label].predicted_impact.timeframe }}</span>
                  <span :class="['impact-confidence', aiAnalysisData[cause.root_cause_label].predicted_impact.confidence?.toLowerCase()]">
                    {{ aiAnalysisData[cause.root_cause_label].predicted_impact.confidence }} Confidence
                  </span>
                </div>
              </div>
            </template>

            <div v-else class="ai-error">
              Failed to load AI analysis. Click to retry.
            </div>
          </div>
        </div>

        <!-- Suggested Actions -->
        <div style="background: var(--td-green-light); border-radius: 6px; padding: 12px;">
          <div style="font-size: 12px; font-weight: 600; color: var(--td-green); margin-bottom: 8px; text-transform: uppercase;">
            Suggested Actions
          </div>
          <ul style="list-style: none; padding: 0;">
            <li v-for="(action, i) in cause.suggested_actions" :key="i" style="margin-bottom: 8px; font-size: 13px;">
              <span :class="['action-tag', action.type.toLowerCase()]">{{ action.type }}</span>
              {{ action.text }}
            </li>
          </ul>
        </div>
      </div>
    </template>

    <div v-else class="empty-state">
      No analysis results available
    </div>

    <!-- Data Table Modal -->
    <DataTableModal
      :show="showExportModal"
      :title="exportModalTitle"
      :labels="exportModalLabels"
      :rows="exportModalRows"
      row-label="Metric"
      @close="showExportModal = false"
    />
  </div>
</template>

<script setup>
import { ref, reactive, watch } from 'vue'
import DataTableModal from './DataTableModal.vue'
import { getRootCauseTrends, getEnhancedRootCause } from '../services/api'

const props = defineProps({
  result: {
    type: Object,
    default: null
  },
  loading: {
    type: Boolean,
    default: false
  },
  filters: {
    type: Object,
    default: () => ({})
  }
})

const trendData = reactive({})
const loadingTrends = reactive({})
const showExportModal = ref(false)
const exportModalTitle = ref('')
const exportModalLabels = ref([])
const exportModalRows = ref([])

// AI Analysis state
const expandedAnalysis = reactive({})
const loadingAIAnalysis = reactive({})
const aiAnalysisData = reactive({})

// Watch for result changes to load trends
watch(() => props.result, async (newResult) => {
  if (newResult?.root_causes) {
    for (const cause of newResult.root_causes) {
      await loadTrendForCause(cause.root_cause_label)
    }
  }
}, { immediate: true })

async function loadTrendForCause(rootCauseLabel) {
  if (trendData[rootCauseLabel] || loadingTrends[rootCauseLabel]) return

  loadingTrends[rootCauseLabel] = true
  try {
    const data = await getRootCauseTrends(rootCauseLabel, props.filters, 8)
    trendData[rootCauseLabel] = data
  } catch (error) {
    console.error(`Failed to load trend for ${rootCauseLabel}:`, error)
  } finally {
    loadingTrends[rootCauseLabel] = false
  }
}

function getTrendChartOptions(rootCauseLabel) {
  const data = trendData[rootCauseLabel]
  if (!data) return {}

  return {
    chart: {
      type: 'bar',
      toolbar: { show: false },
      sparkline: { enabled: false }
    },
    plotOptions: {
      bar: {
        borderRadius: 3,
        columnWidth: '60%'
      }
    },
    colors: ['#00843D'],
    dataLabels: { enabled: false },
    xaxis: {
      categories: data.labels.map(l => l.replace(/^\d{4}-/, '')),
      labels: {
        style: { fontSize: '10px', colors: '#6B7280' }
      }
    },
    yaxis: {
      labels: {
        style: { fontSize: '10px', colors: '#6B7280' }
      }
    },
    grid: {
      borderColor: '#E5E7EB',
      strokeDashArray: 2,
      padding: { left: 0, right: 0 }
    },
    tooltip: {
      y: {
        formatter: (val) => `${val} complaints`
      }
    }
  }
}

function getTrendChartSeries(rootCauseLabel) {
  const data = trendData[rootCauseLabel]
  if (!data) return []

  return [{
    name: 'Complaints',
    data: data.values
  }]
}

function getWowClass(change) {
  if (change === null || change === undefined) return 'neutral'
  // For root causes, lower is better
  return change < 0 ? 'positive' : 'negative'
}

function openExportModal(cause) {
  const data = trendData[cause.root_cause_label]
  if (!data) {
    alert('Trend data not available yet')
    return
  }

  exportModalTitle.value = `${cause.root_cause_label} - Weekly Data`
  exportModalLabels.value = data.labels
  exportModalRows.value = [
    { name: 'Count', values: data.values },
    { name: '% of Total', values: data.percentages }
  ]
  showExportModal.value = true
}

function formatSummary(text) {
  if (!text) return ''
  return text.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
}

// AI Analysis functions
async function toggleAIAnalysis(rootCauseLabel) {
  expandedAnalysis[rootCauseLabel] = !expandedAnalysis[rootCauseLabel]

  // Load AI analysis if expanding and not already loaded
  if (expandedAnalysis[rootCauseLabel] && !aiAnalysisData[rootCauseLabel]) {
    await loadAIAnalysis(rootCauseLabel)
  }
}

async function loadAIAnalysis(rootCauseLabel) {
  if (loadingAIAnalysis[rootCauseLabel]) return

  loadingAIAnalysis[rootCauseLabel] = true
  try {
    const response = await getEnhancedRootCause(rootCauseLabel, props.filters)
    if (response.success && response.root_cause?.ai_analysis) {
      aiAnalysisData[rootCauseLabel] = response.root_cause.ai_analysis
    }
  } catch (error) {
    console.error(`Failed to load AI analysis for ${rootCauseLabel}:`, error)
    aiAnalysisData[rootCauseLabel] = null
  } finally {
    loadingAIAnalysis[rootCauseLabel] = false
  }
}

function formatAnalysisSummary(text) {
  if (!text) return ''
  // Convert newlines to <br> and handle bullet points
  return text
    .replace(/\n/g, '<br>')
    .replace(/•/g, '&bull;')
}
</script>

<style scoped>
.export-btn {
  padding: 4px 10px;
  font-size: 11px;
  font-weight: 500;
  background: white;
  border: 1px solid var(--td-gray-300);
  border-radius: 4px;
  color: var(--td-gray-600);
  cursor: pointer;
  transition: all 0.2s;
}

.export-btn:hover {
  background: var(--td-gray-50);
  border-color: var(--td-gray-400);
}

.trend-section {
  background: var(--td-gray-50);
  border-radius: 8px;
  padding: 12px;
  margin-bottom: 16px;
}

.trend-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.trend-title {
  font-size: 12px;
  font-weight: 600;
  color: var(--td-gray-600);
  text-transform: uppercase;
}

.trend-loading {
  background: var(--td-gray-50);
  border-radius: 8px;
  padding: 24px;
  margin-bottom: 16px;
  text-align: center;
  font-size: 12px;
  color: var(--td-gray-500);
}

.wow-badge {
  font-size: 11px;
  font-weight: 600;
  padding: 3px 8px;
  border-radius: 10px;
}

.wow-badge.positive {
  background: #D1FAE5;
  color: #047857;
}

.wow-badge.negative {
  background: #FEE2E2;
  color: #B91C1C;
}

.wow-badge.neutral {
  background: var(--td-gray-200);
  color: var(--td-gray-600);
}

/* AI Analysis Section Styles */
.ai-analysis-section {
  margin-bottom: 16px;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  overflow: hidden;
}

.ai-analysis-toggle {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  background: linear-gradient(135deg, #f0f9ff 0%, #f8fafc 100%);
  border: none;
  cursor: pointer;
  font-size: 13px;
  font-weight: 600;
  color: #1e293b;
  transition: background 0.2s;
}

.ai-analysis-toggle:hover {
  background: linear-gradient(135deg, #e0f2fe 0%, #f1f5f9 100%);
}

.ai-analysis-toggle.expanded {
  border-bottom: 1px solid #e2e8f0;
}

.ai-analysis-toggle .ai-icon {
  font-size: 16px;
}

.ai-analysis-toggle .toggle-arrow {
  margin-left: auto;
  font-size: 10px;
  color: #64748b;
}

.ai-analysis-content {
  padding: 16px;
  background: white;
}

.ai-loading {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 24px;
  color: #64748b;
  font-size: 13px;
}

.ai-loading-spinner {
  width: 18px;
  height: 18px;
  border: 2px solid #e2e8f0;
  border-top-color: var(--td-green);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.ai-error {
  text-align: center;
  padding: 24px;
  color: #dc2626;
  font-size: 13px;
}

.ai-sub-section {
  margin-bottom: 16px;
  padding-bottom: 16px;
  border-bottom: 1px solid #f1f5f9;
}

.ai-sub-section:last-child {
  margin-bottom: 0;
  padding-bottom: 0;
  border-bottom: none;
}

.ai-sub-title {
  margin: 0 0 12px 0;
  font-size: 12px;
  font-weight: 600;
  color: #475569;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

/* Sub-Issues */
.sub-issues-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.sub-issue-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.sub-issue-bar {
  height: 8px;
  background: #e2e8f0;
  border-radius: 4px;
  overflow: hidden;
}

.sub-issue-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--td-green) 0%, #22c55e 100%);
  border-radius: 4px;
  transition: width 0.3s ease;
}

.sub-issue-label {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
}

.sub-issue-name {
  color: #334155;
}

.sub-issue-pct {
  font-weight: 600;
  color: #475569;
}

/* Correlations */
.correlations-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.correlation-item {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  padding: 8px 12px;
  background: #f8fafc;
  border-radius: 6px;
  font-size: 12px;
}

.corr-factor {
  font-weight: 600;
  color: #475569;
}

.corr-value {
  color: var(--td-green);
  font-weight: 500;
}

.corr-insight {
  flex-basis: 100%;
  color: #64748b;
  font-style: italic;
}

/* AI Insight */
.ai-insight-text {
  margin: 0;
  font-size: 13px;
  line-height: 1.7;
  color: #334155;
  white-space: pre-wrap;
}

/* Personalized Actions */
.personalized-actions {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.personalized-action {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  padding: 10px 12px;
  background: #f8fafc;
  border-radius: 6px;
  border-left: 3px solid transparent;
}

.personalized-action:has(.priority-badge.critical) {
  border-left-color: #dc2626;
  background: #fef2f2;
}

.personalized-action:has(.priority-badge.high) {
  border-left-color: #f59e0b;
  background: #fffbeb;
}

.personalized-action:has(.priority-badge.medium) {
  border-left-color: #3b82f6;
  background: #eff6ff;
}

.priority-badge {
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 10px;
  font-weight: 600;
  text-transform: uppercase;
  white-space: nowrap;
}

.priority-badge.critical {
  background: #dc2626;
  color: white;
}

.priority-badge.high {
  background: #f59e0b;
  color: white;
}

.priority-badge.medium {
  background: #3b82f6;
  color: white;
}

.priority-badge.low {
  background: #64748b;
  color: white;
}

.personalized-action .action-text {
  flex: 1;
  font-size: 13px;
  color: #334155;
  line-height: 1.4;
}

.action-type-tag {
  padding: 2px 6px;
  background: #e2e8f0;
  border-radius: 3px;
  font-size: 10px;
  color: #475569;
  white-space: nowrap;
}

/* Predicted Impact */
.predicted-impact {
  background: linear-gradient(135deg, #f0fdf4 0%, #ecfdf5 100%);
  border: 1px solid #bbf7d0;
  border-radius: 8px;
  padding: 14px;
}

.impact-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.impact-icon {
  font-size: 16px;
}

.impact-title {
  font-size: 12px;
  font-weight: 600;
  color: #166534;
  text-transform: uppercase;
}

.impact-message {
  margin: 0 0 10px 0;
  font-size: 13px;
  color: #166534;
  line-height: 1.5;
}

.impact-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  font-size: 11px;
}

.impact-reduction {
  font-weight: 600;
  color: #15803d;
}

.impact-timeframe {
  color: #64748b;
}

.impact-confidence {
  padding: 2px 8px;
  border-radius: 10px;
  font-weight: 500;
}

.impact-confidence.high {
  background: #dcfce7;
  color: #166534;
}

.impact-confidence.medium {
  background: #fef3c7;
  color: #92400e;
}

.impact-confidence.low {
  background: #fecaca;
  color: #991b1b;
}
</style>
