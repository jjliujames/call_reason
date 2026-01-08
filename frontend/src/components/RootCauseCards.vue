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
          <div style="display: flex; gap: 8px;">
            <span class="badge badge-yellow">Impact: {{ cause.impact_score }}</span>
            <span :class="['concentration-badge', cause.concentration === 'Systemic' ? 'systemic' : 'concentrated']">
              {{ cause.concentration }}
            </span>
          </div>
        </div>

        <p style="font-size: 13px; color: var(--td-gray-600); margin-bottom: 16px;">
          {{ cause.description }}
        </p>

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
  </div>
</template>

<script setup>
defineProps({
  result: {
    type: Object,
    default: null
  },
  loading: {
    type: Boolean,
    default: false
  }
})

function formatSummary(text) {
  if (!text) return ''
  return text.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
}
</script>
