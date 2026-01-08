<template>
  <div>
    <BreadcrumbBar :crumbs="[{ label: 'Actions & Opportunities' }]" />

    <div class="page-header">
      <h1 class="page-title">Actions & Opportunities</h1>
      <p class="page-subtitle">Prioritized recommendations to improve call center performance</p>
    </div>

    <div class="page-content">
      <!-- Summary Cards -->
      <div class="kpi-grid">
        <div class="kpi-card highlight">
          <div class="kpi-label">Total Actions</div>
          <div class="kpi-value">{{ allActions.length }}</div>
        </div>
        <div class="kpi-card" style="border-left-color: #EAB308;">
          <div class="kpi-label">Policy Actions</div>
          <div class="kpi-value">{{ actionsByType.Policy?.length || 0 }}</div>
        </div>
        <div class="kpi-card" style="border-left-color: #2563EB;">
          <div class="kpi-label">Process Actions</div>
          <div class="kpi-value">{{ actionsByType.Process?.length || 0 }}</div>
        </div>
        <div class="kpi-card" style="border-left-color: #00843D;">
          <div class="kpi-label">Digital Actions</div>
          <div class="kpi-value">{{ actionsByType.Digital?.length || 0 }}</div>
        </div>
      </div>

      <!-- No data state -->
      <div v-if="!rootCauseResult" class="placeholder-page">
        <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="var(--td-gray-400)" stroke-width="1.5">
          <path d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4"/>
        </svg>
        <h2>No Actions Available</h2>
        <p>Run a Root Cause Analysis first to generate recommended actions.</p>
        <button class="btn btn-primary" style="margin-top: 16px;" @click="goToRootCause">
          Go to Root Cause Analysis
        </button>
      </div>

      <template v-else>
        <!-- Filter by Type -->
        <div class="card" style="margin-bottom: 24px;">
          <div class="card-body">
            <div style="display: flex; gap: 8px; flex-wrap: wrap;">
              <button
                :class="['btn', selectedType === '' ? 'btn-primary' : 'btn-secondary']"
                @click="selectedType = ''"
              >
                All ({{ allActions.length }})
              </button>
              <button
                v-for="type in ['Policy', 'Process', 'Digital', 'Training']"
                :key="type"
                :class="['btn', selectedType === type ? 'btn-primary' : 'btn-secondary']"
                @click="selectedType = type"
              >
                {{ type }} ({{ actionsByType[type]?.length || 0 }})
              </button>
            </div>
          </div>
        </div>

        <!-- Actions List -->
        <div class="card">
          <div class="card-header">
            <span class="card-title">Recommended Actions</span>
            <span style="font-size: 13px; color: var(--td-gray-600);">
              Sorted by impact score
            </span>
          </div>

          <div style="max-height: 600px; overflow-y: auto;">
            <div
              v-for="(action, index) in filteredActions"
              :key="index"
              style="padding: 20px; border-bottom: 1px solid var(--td-gray-200);"
            >
              <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 12px;">
                <div style="display: flex; align-items: center; gap: 12px;">
                  <span style="width: 28px; height: 28px; background: var(--td-gray-200); border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 12px; font-weight: 600;">
                    {{ index + 1 }}
                  </span>
                  <span :class="['action-tag', action.type.toLowerCase()]">{{ action.type }}</span>
                </div>
                <div style="display: flex; gap: 8px;">
                  <span class="badge badge-yellow">Impact: {{ action.impactScore }}</span>
                  <span :class="['concentration-badge', action.concentration === 'Systemic' ? 'systemic' : 'concentrated']">
                    {{ action.concentration }}
                  </span>
                </div>
              </div>

              <h4 style="font-size: 15px; font-weight: 600; margin-bottom: 8px;">{{ action.text }}</h4>

              <p style="font-size: 13px; color: var(--td-gray-600); margin-bottom: 12px;">
                Related to: <strong>{{ action.rootCause }}</strong>
              </p>

              <div style="display: flex; gap: 24px; font-size: 13px; color: var(--td-gray-600);">
                <span>{{ action.frequency }} complaints</span>
                <span>{{ action.avgHandleTime }} min avg handle time</span>
                <span>{{ action.fcrRate }}% FCR</span>
              </div>

              <div style="margin-top: 12px; display: flex; gap: 8px;">
                <button class="btn btn-secondary btn-sm" @click="markInProgress(action)">
                  Mark In Progress
                </button>
                <button class="btn btn-secondary btn-sm" @click="viewRelatedComplaints(action)">
                  View Related Complaints
                </button>
              </div>
            </div>
          </div>

          <div v-if="!filteredActions.length" class="empty-state">
            No actions match the selected filter
          </div>
        </div>

        <!-- Digital Opportunities -->
        <div class="card" style="margin-top: 24px;">
          <div class="card-header">
            <span class="card-title">Digital Deflection Opportunities</span>
          </div>
          <div class="card-body">
            <p style="font-size: 14px; color: var(--td-gray-700); margin-bottom: 16px;">
              Based on the analysis, these call types have high digital eligibility but low deflection success rates.
              Improving self-service for these areas could significantly reduce call volume.
            </p>

            <div class="grid-3">
              <div style="padding: 16px; background: var(--td-green-light); border-radius: 8px;">
                <div style="font-size: 24px; font-weight: 700; color: var(--td-green);">
                  {{ digitalOpportunities.eligible.toLocaleString() }}
                </div>
                <div style="font-size: 12px; color: var(--td-gray-600); text-transform: uppercase;">
                  Digital Eligible Calls
                </div>
              </div>
              <div style="padding: 16px; background: var(--td-orange-light); border-radius: 8px;">
                <div style="font-size: 24px; font-weight: 700; color: var(--td-orange);">
                  {{ digitalOpportunities.failureRate }}%
                </div>
                <div style="font-size: 12px; color: var(--td-gray-600); text-transform: uppercase;">
                  Deflection Failure Rate
                </div>
              </div>
              <div style="padding: 16px; background: var(--td-blue-light); border-radius: 8px;">
                <div style="font-size: 24px; font-weight: 700; color: var(--td-blue);">
                  ${{ digitalOpportunities.potentialSavings.toLocaleString() }}
                </div>
                <div style="font-size: 12px; color: var(--td-gray-600); text-transform: uppercase;">
                  Potential Monthly Savings
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Training Priorities -->
        <div class="card" style="margin-top: 24px;">
          <div class="card-header">
            <span class="card-title">Agent Training Priorities</span>
          </div>
          <div class="card-body">
            <p style="font-size: 14px; color: var(--td-gray-700); margin-bottom: 16px;">
              These agents have been identified as having concentrated complaint patterns
              and would benefit from targeted coaching.
            </p>

            <div v-if="trainingPriorities.length" style="display: flex; flex-direction: column; gap: 12px;">
              <div
                v-for="agent in trainingPriorities"
                :key="agent.agent_id"
                style="display: flex; align-items: center; gap: 16px; padding: 12px; background: var(--td-gray-100); border-radius: 8px;"
              >
                <div style="flex: 1;">
                  <div style="font-weight: 600;">{{ agent.agent_name }}</div>
                  <div style="font-size: 12px; color: var(--td-gray-600);">
                    {{ agent.team_leader }} · {{ agent.region }}
                  </div>
                </div>
                <div style="text-align: right;">
                  <div style="font-size: 13px;">
                    <span class="badge badge-red">{{ agent.complaint_count }} complaints</span>
                  </div>
                  <div style="font-size: 12px; color: var(--td-gray-500); margin-top: 4px;">
                    Focus: {{ agent.focus_area }}
                  </div>
                </div>
              </div>
            </div>

            <div v-else class="empty-state">
              No specific training priorities identified
            </div>
          </div>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import BreadcrumbBar from '../components/BreadcrumbBar.vue'
import { useMainStore } from '../stores/main'

const router = useRouter()
const store = useMainStore()

const selectedType = ref('')
const rootCauseResult = computed(() => store.lastRootCauseResult)

// Extract all actions from root causes
const allActions = computed(() => {
  if (!rootCauseResult.value?.root_causes) return []

  const actions = []
  for (const cause of rootCauseResult.value.root_causes) {
    for (const action of cause.suggested_actions || []) {
      actions.push({
        ...action,
        rootCause: cause.root_cause_label,
        impactScore: cause.impact_score,
        concentration: cause.concentration,
        frequency: cause.frequency,
        avgHandleTime: cause.avg_handling_time_minutes,
        fcrRate: cause.fcr_rate,
        topAgents: cause.top_agents
      })
    }
  }

  // Sort by impact score
  actions.sort((a, b) => b.impactScore - a.impactScore)
  return actions
})

const actionsByType = computed(() => {
  const grouped = {}
  for (const action of allActions.value) {
    if (!grouped[action.type]) {
      grouped[action.type] = []
    }
    grouped[action.type].push(action)
  }
  return grouped
})

const filteredActions = computed(() => {
  if (!selectedType.value) return allActions.value
  return allActions.value.filter(a => a.type === selectedType.value)
})

// Mock digital opportunities data
const digitalOpportunities = computed(() => ({
  eligible: 2450,
  failureRate: 62,
  potentialSavings: 18500
}))

// Training priorities from concentrated causes
const trainingPriorities = computed(() => {
  if (!rootCauseResult.value?.root_causes) return []

  const agentMap = new Map()

  for (const cause of rootCauseResult.value.root_causes) {
    if (cause.concentration === 'Agent-Concentrated' && cause.top_agents) {
      for (const agent of cause.top_agents.slice(0, 2)) {
        if (!agentMap.has(agent.agent_id)) {
          agentMap.set(agent.agent_id, {
            ...agent,
            complaint_count: agent.count,
            focus_area: cause.root_cause_label,
            team_leader: 'Team Leader', // Would come from agent data
            region: 'Region' // Would come from agent data
          })
        }
      }
    }
  }

  return Array.from(agentMap.values()).slice(0, 5)
})

function goToRootCause() {
  router.push('/root-cause')
}

function markInProgress(action) {
  alert(`Marked "${action.text}" as In Progress. In a real app, this would update a task tracking system.`)
}

function viewRelatedComplaints(action) {
  // Navigate to complaints view filtered by root cause
  router.push('/complaints')
}

onMounted(() => {
  // Check if we have results
  if (!rootCauseResult.value) {
    // Could auto-navigate to root cause page
  }
})
</script>
