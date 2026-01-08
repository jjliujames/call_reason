<template>
  <div>
    <BreadcrumbBar :crumbs="breadcrumbs" />

    <div v-if="loading" class="loading" style="padding: 60px;">Loading interaction details...</div>

    <template v-else-if="interaction">
      <!-- Global Header -->
      <div class="page-header">
        <div style="display: flex; justify-content: space-between; align-items: flex-start;">
          <div>
            <h1 class="page-title">Interaction {{ interaction.interaction_id.slice(0, 8) }}...</h1>
            <p class="page-subtitle">{{ formatFullTimestamp(interaction.timestamp) }}</p>
          </div>
          <div>
            <button class="listen-btn" @click="openCallRecording">
              <span class="listen-icon">🎧</span>
              Listen to Call
            </button>
          </div>
        </div>
        <div class="header-badges">
          <span class="badge badge-blue">{{ interaction.channel }}</span>
          <span class="badge badge-gray">{{ interaction.customer_segment }}</span>
          <span v-if="interaction.is_complaint" class="badge badge-red">Complaint</span>
          <span v-if="interaction.is_complaint" :class="['badge', severityClass]">
            {{ interaction.complaint_severity }} Severity
          </span>
          <span v-if="interaction.escalated" class="badge badge-orange">Escalated</span>
          <span v-if="interaction.revenue_at_risk_flag" class="badge badge-red">Revenue at Risk</span>
        </div>
      </div>

      <div class="page-content">
        <!-- 3-Column Layout -->
        <div class="detail-grid">
          <!-- LEFT COLUMN: Context & Taxonomy -->
          <div class="detail-column">
            <!-- Interaction Summary Card -->
            <div class="card">
              <div class="card-header">
                <span class="card-title">Interaction Summary</span>
              </div>
              <div class="card-body">
                <div class="info-list">
                  <div class="info-item">
                    <span class="info-label">Agent</span>
                    <span class="info-value">
                      <span class="link" @click="navigateToAgent">{{ interaction.agent_name }}</span>
                      <br><small style="color: var(--td-gray-500);">{{ interaction.agent_id }}</small>
                    </span>
                  </div>
                  <div class="info-item">
                    <span class="info-label">Team Leader</span>
                    <span class="info-value">{{ interaction.team_leader }}</span>
                  </div>
                  <div class="info-item">
                    <span class="info-label">Region</span>
                    <span class="info-value">{{ interaction.region }}</span>
                  </div>
                  <div class="info-item">
                    <span class="info-label">Tenure</span>
                    <span class="info-value">{{ interaction.tenure_band }}</span>
                  </div>
                  <div class="info-item">
                    <span class="info-label">Line of Business</span>
                    <span class="info-value">{{ interaction.line_of_business }}</span>
                  </div>
                  <div class="info-item">
                    <span class="info-label">Call Reason</span>
                    <span class="info-value">{{ interaction.call_reason }}</span>
                  </div>
                  <div class="info-item">
                    <span class="info-label">Product</span>
                    <span class="info-value">{{ interaction.product }}</span>
                  </div>
                </div>
              </div>
            </div>

            <!-- Taxonomy Path Card -->
            <div class="card">
              <div class="card-header">
                <span class="card-title">Taxonomy Path</span>
              </div>
              <div class="card-body">
                <div style="display: flex; flex-direction: column; gap: 8px;">
                  <div>
                    <span class="link" @click="navigateToLob">{{ interaction.line_of_business }}</span>
                    <span style="color: var(--td-gray-400); margin: 0 8px;">→</span>
                  </div>
                  <div style="padding-left: 16px;">
                    <span class="link" @click="navigateToCallReason">{{ interaction.call_reason }}</span>
                    <span style="color: var(--td-gray-400); margin: 0 8px;">→</span>
                  </div>
                  <div style="padding-left: 32px;">
                    <span class="link" @click="navigateToProduct">{{ interaction.product }}</span>
                    <span style="color: var(--td-gray-400); margin: 0 8px;">→</span>
                  </div>
                  <div style="padding-left: 48px;">
                    <span class="link" @click="navigateToAgent">{{ interaction.agent_name }}</span>
                  </div>
                </div>
              </div>
            </div>

            <!-- Complaint Info Card (only if complaint) -->
            <div class="card" v-if="interaction.is_complaint">
              <div class="card-header">
                <span class="card-title">Complaint Information</span>
              </div>
              <div class="card-body">
                <div class="info-list">
                  <div class="info-item">
                    <span class="info-label">Category</span>
                    <span class="info-value">{{ interaction.complaint_category }}</span>
                  </div>
                  <div class="info-item">
                    <span class="info-label">Severity</span>
                    <span :class="['badge', severityClass]">{{ interaction.complaint_severity }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- CENTER COLUMN: Narrative & AI Insights -->
          <div class="detail-column">
            <!-- Complaint Text / Notes -->
            <div class="card">
              <div class="card-header">
                <span class="card-title">
                  {{ interaction.is_complaint ? 'Customer Complaint' : 'Interaction Notes' }}
                </span>
              </div>
              <div class="card-body">
                <p style="font-size: 14px; line-height: 1.7; color: var(--td-gray-800);">
                  {{ interaction.is_complaint ? interaction.complaint_text : (interaction.agent_notes || 'No notes recorded.') }}
                </p>
              </div>
            </div>

            <!-- Agent Notes (if exists and is complaint) -->
            <div class="card" v-if="interaction.is_complaint && interaction.agent_notes">
              <div class="card-header">
                <span class="card-title">Agent Notes</span>
              </div>
              <div class="card-body">
                <p style="font-size: 14px; line-height: 1.7; color: var(--td-gray-700);">
                  {{ interaction.agent_notes }}
                </p>
              </div>
            </div>

            <!-- Call Transcript Card -->
            <div class="card">
              <div class="card-header">
                <span class="card-title">Call Transcript</span>
                <div style="display: flex; gap: 8px; align-items: center;">
                  <span class="badge badge-blue">{{ Math.round(interaction.handling_time_seconds / 60) }} min</span>
                  <button class="btn-sm" @click="openCallRecording">🎧 Listen</button>
                </div>
              </div>
              <div class="card-body transcript-body">
                <div class="transcript-container">
                  <div v-for="(line, index) in callTranscript" :key="index" class="transcript-line">
                    <div class="transcript-speaker" :class="line.speaker === 'Agent' ? 'agent' : 'customer'">
                      <span class="speaker-label">{{ line.speaker }}</span>
                      <span class="transcript-time">{{ line.time }}</span>
                    </div>
                    <div class="transcript-text">{{ line.text }}</div>
                  </div>
                </div>
              </div>
            </div>

            <!-- AI Summary Card -->
            <div class="card" style="border-left: 4px solid var(--td-green);">
              <div class="card-header">
                <span class="card-title">AI Summary (Simulated)</span>
                <span class="badge badge-green">AI Generated</span>
              </div>
              <div class="card-body">
                <ul class="bullet-list">
                  <li v-for="(bullet, i) in interaction.ai_summary" :key="i">{{ bullet }}</li>
                </ul>
              </div>
            </div>

            <!-- Detected Root Cause Card -->
            <div class="card">
              <div class="card-header">
                <span class="card-title">Detected Root Cause</span>
                <span class="badge badge-blue">{{ Math.round(interaction.root_cause_confidence * 100) }}% confidence</span>
              </div>
              <div class="card-body">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                  <span style="font-size: 16px; font-weight: 600; color: var(--td-gray-900);">
                    {{ interaction.root_cause_label }}
                  </span>
                  <span :class="['concentration-badge', interaction.root_cause_concentration === 'Systemic' ? 'systemic' : 'concentrated']">
                    {{ interaction.root_cause_concentration }}
                  </span>
                </div>
                <p style="font-size: 13px; color: var(--td-gray-600); margin-bottom: 12px;">
                  This root cause has {{ interaction.root_cause_total_count }} total complaints.
                  <span v-if="interaction.root_cause_concentration === 'Agent-Concentrated'">
                    Top 3 agents account for 40%+ of cases.
                  </span>
                </p>
                <div v-if="interaction.root_cause_top_agents?.length" style="display: flex; gap: 8px; flex-wrap: wrap;">
                  <span v-for="agent in interaction.root_cause_top_agents.slice(0, 3)" :key="agent.agent_id" class="badge badge-gray">
                    {{ agent.agent_name }} ({{ agent.count }})
                  </span>
                </div>
              </div>
            </div>

            <!-- Recommended Actions Card -->
            <div class="card" style="background: var(--td-green-light);">
              <div class="card-header" style="background: transparent; border-bottom-color: rgba(0,132,61,0.2);">
                <span class="card-title" style="color: var(--td-green);">Recommended Actions</span>
              </div>
              <div class="card-body">
                <ul style="list-style: none; padding: 0;">
                  <li v-for="(action, i) in interaction.recommended_actions" :key="i" style="margin-bottom: 12px; font-size: 14px;">
                    <span :class="['action-tag', action.type.toLowerCase()]">{{ action.type }}</span>
                    {{ action.text }}
                  </li>
                </ul>
              </div>
            </div>
          </div>

          <!-- RIGHT COLUMN: Operational Metrics -->
          <div class="detail-column">
            <!-- KPI List Card -->
            <div class="card">
              <div class="card-header">
                <span class="card-title">Operational Metrics</span>
              </div>
              <div class="card-body">
                <div class="info-list">
                  <div class="info-item">
                    <span class="info-label">Handling Time</span>
                    <span class="info-value" style="font-size: 18px; font-weight: 600;">
                      {{ Math.round(interaction.handling_time_seconds / 60) }} min
                    </span>
                  </div>
                  <div class="info-item">
                    <span class="info-label">Hold Time</span>
                    <span class="info-value">{{ Math.round(interaction.hold_time_seconds / 60) }} min</span>
                  </div>
                  <div class="info-item">
                    <span class="info-label">Transfers</span>
                    <span class="info-value">{{ interaction.transfer_count }}</span>
                  </div>
                  <div class="info-item">
                    <span class="info-label">Escalated</span>
                    <span :class="['badge', interaction.escalated ? 'badge-orange' : 'badge-gray']">
                      {{ interaction.escalated ? 'Yes' : 'No' }}
                    </span>
                  </div>
                  <div class="info-item">
                    <span class="info-label">Disposition</span>
                    <span class="info-value">{{ interaction.disposition }}</span>
                  </div>
                  <div class="info-item">
                    <span class="info-label">First Contact Resolution</span>
                    <span :class="['badge', interaction.resolved_on_first_contact ? 'badge-green' : 'badge-red']">
                      {{ interaction.resolved_on_first_contact ? 'Yes' : 'No' }}
                    </span>
                  </div>
                </div>
              </div>
            </div>

            <!-- Digital Box -->
            <div class="card">
              <div class="card-header">
                <span class="card-title">Digital Opportunity</span>
              </div>
              <div class="card-body">
                <div class="info-list">
                  <div class="info-item">
                    <span class="info-label">Digital Eligible</span>
                    <span :class="['badge', interaction.digital_eligible ? 'badge-blue' : 'badge-gray']">
                      {{ interaction.digital_eligible ? 'Yes' : 'No' }}
                    </span>
                  </div>
                  <div class="info-item" v-if="interaction.digital_eligible">
                    <span class="info-label">Deflection Attempted</span>
                    <span class="info-value">{{ interaction.deflection_attempted ? 'Yes' : 'No' }}</span>
                  </div>
                  <div class="info-item" v-if="interaction.deflection_attempted">
                    <span class="info-label">Deflection Success</span>
                    <span :class="['badge', interaction.deflection_success ? 'badge-green' : 'badge-red']">
                      {{ interaction.deflection_success ? 'Yes' : 'No' }}
                    </span>
                  </div>
                  <div class="info-item" v-if="interaction.digital_eligible && !interaction.deflection_success && interaction.digital_failure_reason">
                    <span class="info-label">Failure Reason</span>
                    <span class="info-value" style="color: var(--td-red);">{{ interaction.digital_failure_reason }}</span>
                  </div>
                </div>
              </div>
            </div>

            <!-- Revenue Box -->
            <div class="card">
              <div class="card-header">
                <span class="card-title">Revenue Impact</span>
              </div>
              <div class="card-body">
                <div class="info-list">
                  <div class="info-item">
                    <span class="info-label">Revenue at Risk</span>
                    <span :class="['badge', interaction.revenue_at_risk_flag ? 'badge-red' : 'badge-gray']">
                      {{ interaction.revenue_at_risk_flag ? 'Yes' : 'No' }}
                    </span>
                  </div>
                  <div class="info-item">
                    <span class="info-label">Revenue Opportunity</span>
                    <span :class="['badge', interaction.revenue_opportunity_flag ? 'badge-green' : 'badge-gray']">
                      {{ interaction.revenue_opportunity_flag ? 'Yes' : 'No' }}
                    </span>
                  </div>
                  <div class="info-item">
                    <span class="info-label">Estimated Cost</span>
                    <span class="info-value" style="font-size: 18px; font-weight: 600; color: var(--td-red);">
                      ${{ interaction.estimated_cost_dollars.toFixed(2) }}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- BOTTOM SECTION: Related Interactions -->
        <div class="card" style="margin-top: 24px;">
          <div class="tabs">
            <button
              class="tab"
              :class="{ active: activeRelatedTab === 'same_reason_product' }"
              @click="loadRelated('same_reason_product')"
            >
              Same Call Reason & Product
            </button>
            <button
              class="tab"
              :class="{ active: activeRelatedTab === 'same_agent' }"
              @click="loadRelated('same_agent')"
            >
              Same Agent
            </button>
            <button
              class="tab"
              :class="{ active: activeRelatedTab === 'same_complaint_category' }"
              @click="loadRelated('same_complaint_category')"
              :disabled="!interaction.is_complaint"
            >
              Same Complaint Category
            </button>
          </div>

          <div class="card-body">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
              <span style="font-size: 13px; color: var(--td-gray-600);">
                {{ relatedInteractions.length }} of {{ relatedTotal }} related interactions
              </span>
              <button
                class="btn btn-primary btn-sm"
                @click="runRootCauseOnRelated"
                :disabled="relatedInteractions.length === 0 || analyzingRelated"
              >
                {{ analyzingRelated ? 'Analyzing...' : 'Run Root Cause Analysis on Related' }}
              </button>
            </div>

            <div v-if="loadingRelated" class="loading">Loading related interactions...</div>

            <table v-else-if="relatedInteractions.length" class="data-table">
              <thead>
                <tr>
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
                  v-for="rel in relatedInteractions"
                  :key="rel.interaction_id"
                  @click="goToInteraction(rel.interaction_id)"
                >
                  <td>{{ formatTimestamp(rel.timestamp) }}</td>
                  <td>{{ rel.agent_name }}</td>
                  <td>{{ rel.call_reason }}</td>
                  <td>{{ truncate(rel.product, 20) }}</td>
                  <td>
                    <span v-if="rel.is_complaint" class="badge badge-red">{{ rel.complaint_severity }}</span>
                    <span v-else class="badge badge-gray">No</span>
                  </td>
                  <td>{{ Math.round(rel.handling_time_seconds / 60) }} min</td>
                  <td>
                    <span :class="['badge', rel.resolved_on_first_contact ? 'badge-green' : 'badge-orange']">
                      {{ rel.resolved_on_first_contact ? 'Yes' : 'No' }}
                    </span>
                  </td>
                </tr>
              </tbody>
            </table>

            <div v-else class="empty-state">No related interactions found</div>

            <!-- Inline Root Cause Results -->
            <div v-if="relatedRootCauseResult" style="margin-top: 24px; border-top: 1px solid var(--td-gray-200); padding-top: 24px;">
              <h3 style="font-size: 16px; font-weight: 600; margin-bottom: 16px;">Root Cause Analysis Results</h3>
              <RootCauseCards :result="relatedRootCauseResult" />
            </div>
          </div>
        </div>
      </div>
    </template>

    <div v-else class="empty-state" style="padding: 60px;">
      Interaction not found
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import BreadcrumbBar from '../components/BreadcrumbBar.vue'
import RootCauseCards from '../components/RootCauseCards.vue'
import { useMainStore } from '../stores/main'
import { getInteractionById, getRelatedInteractions, analyzeRootCauses } from '../services/api'

const route = useRoute()
const router = useRouter()
const store = useMainStore()

const loading = ref(true)
const interaction = ref(null)

const activeRelatedTab = ref('same_reason_product')
const relatedInteractions = ref([])
const relatedTotal = ref(0)
const loadingRelated = ref(false)

const analyzingRelated = ref(false)
const relatedRootCauseResult = ref(null)

const breadcrumbs = computed(() => {
  if (!interaction.value) return [{ label: 'Interactions', to: '/interactions' }]

  return [
    { label: 'Interactions', to: '/interactions' },
    {
      label: interaction.value.line_of_business,
      to: '/call-reasons',
      filters: { lineOfBusiness: interaction.value.line_of_business }
    },
    {
      label: interaction.value.call_reason,
      to: '/call-reasons',
      filters: {
        lineOfBusiness: interaction.value.line_of_business,
        callReason: interaction.value.call_reason
      }
    },
    {
      label: truncate(interaction.value.product, 20),
      to: '/call-reasons',
      filters: {
        lineOfBusiness: interaction.value.line_of_business,
        callReason: interaction.value.call_reason,
        product: interaction.value.product
      }
    },
    { label: `Interaction ${interaction.value.interaction_id.slice(0, 8)}...` }
  ]
})

const severityClass = computed(() => {
  if (!interaction.value?.complaint_severity) return 'badge-gray'
  switch (interaction.value.complaint_severity) {
    case 'High': return 'badge-red'
    case 'Medium': return 'badge-orange'
    case 'Low': return 'badge-yellow'
    default: return 'badge-gray'
  }
})

// Generate fake call transcript based on interaction data
const callTranscript = computed(() => {
  if (!interaction.value) return []

  const i = interaction.value
  const duration = Math.round(i.handling_time_seconds / 60)
  const isComplaint = i.is_complaint
  const callReason = i.call_reason
  const product = i.product
  const agentName = i.agent_name?.split(' ')[0] || 'Agent'

  // Build contextual transcript based on interaction data
  const transcriptTemplates = {
    greeting: [
      { speaker: 'Agent', time: '0:00', text: `Thank you for calling TD Bank, my name is ${agentName}. How may I assist you today?` },
      { speaker: 'Customer', time: '0:08', text: `Hi ${agentName}, I'm calling about my ${product.toLowerCase()}.` }
    ],
    issue: generateIssueDialogue(callReason, product, isComplaint, i.complaint_category),
    resolution: generateResolutionDialogue(i.resolved_on_first_contact, i.escalated, i.transfer_count, duration),
    closing: [
      { speaker: 'Agent', time: formatTranscriptTime(duration - 1), text: i.resolved_on_first_contact
        ? 'Is there anything else I can help you with today?'
        : 'I\'ve escalated this to our specialist team. They\'ll be in touch within 24-48 hours.' },
      { speaker: 'Customer', time: formatTranscriptTime(duration - 0.5), text: i.resolved_on_first_contact
        ? 'No, that\'s all. Thank you for your help!'
        : 'Alright, I\'ll wait for their call. Thanks.' },
      { speaker: 'Agent', time: formatTranscriptTime(duration), text: 'Thank you for banking with TD. Have a great day!' }
    ]
  }

  return [
    ...transcriptTemplates.greeting,
    ...transcriptTemplates.issue,
    ...transcriptTemplates.resolution,
    ...transcriptTemplates.closing
  ]
})

function generateIssueDialogue(callReason, product, isComplaint, complaintCategory) {
  const dialogues = []
  const timeOffset = 0.3

  if (isComplaint) {
    dialogues.push(
      { speaker: 'Customer', time: formatTranscriptTime(timeOffset), text: `I have a serious concern I need addressed. I'm really frustrated with the service I've been receiving.` },
      { speaker: 'Agent', time: formatTranscriptTime(timeOffset + 0.2), text: `I'm sorry to hear that. I completely understand your frustration, and I want to help resolve this for you. Can you tell me more about what happened?` }
    )

    if (complaintCategory === 'Fees & Pricing') {
      dialogues.push(
        { speaker: 'Customer', time: formatTranscriptTime(timeOffset + 0.5), text: `I was charged a fee that I don't think is fair. I've been a customer for years and this seems unreasonable.` },
        { speaker: 'Agent', time: formatTranscriptTime(timeOffset + 0.8), text: `Let me pull up your account and review the charges. I'll see what I can do to help with this.` }
      )
    } else if (complaintCategory === 'Digital Experience') {
      dialogues.push(
        { speaker: 'Customer', time: formatTranscriptTime(timeOffset + 0.5), text: `The app keeps crashing when I try to make transfers. I've tried multiple times and it's very frustrating.` },
        { speaker: 'Agent', time: formatTranscriptTime(timeOffset + 0.8), text: `I apologize for the inconvenience with our app. Let me check if there are any known issues and help you complete your transfer.` }
      )
    } else {
      dialogues.push(
        { speaker: 'Customer', time: formatTranscriptTime(timeOffset + 0.5), text: `The issue has been ongoing and I haven't been able to get it resolved despite multiple attempts.` },
        { speaker: 'Agent', time: formatTranscriptTime(timeOffset + 0.8), text: `I understand, and I'm here to help get this sorted out for you today. Let me look into this right away.` }
      )
    }
  } else {
    // Non-complaint regular inquiry
    if (callReason.includes('Account')) {
      dialogues.push(
        { speaker: 'Customer', time: formatTranscriptTime(timeOffset), text: `I need some information about my account. Can you help me check my recent transactions?` },
        { speaker: 'Agent', time: formatTranscriptTime(timeOffset + 0.3), text: `Of course! I'd be happy to help you with that. Let me pull up your account details.` }
      )
    } else if (callReason.includes('Payment') || callReason.includes('Transfer')) {
      dialogues.push(
        { speaker: 'Customer', time: formatTranscriptTime(timeOffset), text: `I need to make a payment and wanted to confirm the process with your help.` },
        { speaker: 'Agent', time: formatTranscriptTime(timeOffset + 0.3), text: `Sure, I can assist you with that payment. Let me guide you through the process.` }
      )
    } else {
      dialogues.push(
        { speaker: 'Customer', time: formatTranscriptTime(timeOffset), text: `I have a question about my ${product.toLowerCase()} and was hoping you could help clarify something.` },
        { speaker: 'Agent', time: formatTranscriptTime(timeOffset + 0.3), text: `Absolutely, I'm here to help. What would you like to know?` }
      )
    }
  }

  return dialogues
}

function generateResolutionDialogue(resolved, escalated, transfers, duration) {
  const dialogues = []
  const midPoint = duration / 2

  if (transfers > 0) {
    dialogues.push(
      { speaker: 'Agent', time: formatTranscriptTime(midPoint), text: `I'll need to transfer you to a specialist who can better assist with this. Please hold for a moment.` },
      { speaker: 'Customer', time: formatTranscriptTime(midPoint + 0.2), text: `Okay, I'll wait.` },
      { speaker: 'Agent', time: formatTranscriptTime(midPoint + 1), text: `Thank you for holding. I've connected with our specialist team.` }
    )
  }

  if (resolved) {
    dialogues.push(
      { speaker: 'Agent', time: formatTranscriptTime(duration - 2), text: `I've processed your request and everything is now updated in the system.` },
      { speaker: 'Customer', time: formatTranscriptTime(duration - 1.8), text: `Great, that's exactly what I needed. Thank you so much!` }
    )
  } else if (escalated) {
    dialogues.push(
      { speaker: 'Agent', time: formatTranscriptTime(duration - 2), text: `This requires additional review by our management team. I'm escalating this to ensure it gets the attention it deserves.` },
      { speaker: 'Customer', time: formatTranscriptTime(duration - 1.8), text: `I appreciate you taking this seriously.` }
    )
  }

  return dialogues
}

function formatTranscriptTime(minutes) {
  const mins = Math.floor(minutes)
  const secs = Math.round((minutes - mins) * 60)
  return `${mins}:${secs.toString().padStart(2, '0')}`
}

function openCallRecording() {
  // Simulate opening call recording - in real app would open audio player or external system
  alert('Call Recording\n\nIn a production environment, this would open the call recording in your telephony system or audio player.\n\nRecording ID: ' + interaction.value?.interaction_id)
}

async function loadInteraction() {
  loading.value = true
  try {
    const id = route.params.id
    interaction.value = await getInteractionById(id)
    await loadRelated('same_reason_product')
  } catch (error) {
    console.error('Failed to load interaction:', error)
    interaction.value = null
  } finally {
    loading.value = false
  }
}

async function loadRelated(mode) {
  activeRelatedTab.value = mode
  loadingRelated.value = true
  relatedRootCauseResult.value = null

  try {
    const result = await getRelatedInteractions(route.params.id, mode, 20)
    relatedInteractions.value = result.data
    relatedTotal.value = result.total
  } catch (error) {
    console.error('Failed to load related:', error)
    relatedInteractions.value = []
    relatedTotal.value = 0
  } finally {
    loadingRelated.value = false
  }
}

async function runRootCauseOnRelated() {
  analyzingRelated.value = true
  try {
    const ids = relatedInteractions.value.map(i => i.interaction_id)
    const result = await analyzeRootCauses({ interaction_ids: ids })
    relatedRootCauseResult.value = result
    store.setLastRootCauseResult(result)
  } catch (error) {
    console.error('Failed to analyze:', error)
  } finally {
    analyzingRelated.value = false
  }
}

function goToInteraction(id) {
  router.push(`/interactions/${id}`)
}

function navigateToLob() {
  store.setGlobalFilters({ lineOfBusiness: interaction.value.line_of_business })
  router.push('/call-reasons')
}

function navigateToCallReason() {
  store.setGlobalFilters({
    lineOfBusiness: interaction.value.line_of_business,
    callReason: interaction.value.call_reason
  })
  router.push('/call-reasons')
}

function navigateToProduct() {
  store.setGlobalFilters({
    lineOfBusiness: interaction.value.line_of_business,
    callReason: interaction.value.call_reason,
    product: interaction.value.product
  })
  router.push('/call-reasons')
}

function navigateToAgent() {
  store.setGlobalFilters({ agentId: interaction.value.agent_id })
  router.push('/agents')
}

function formatFullTimestamp(ts) {
  const date = new Date(ts)
  return date.toLocaleString('en-US', {
    weekday: 'long',
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
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

onMounted(() => {
  loadInteraction()
})

watch(() => route.params.id, () => {
  loadInteraction()
})
</script>

<style scoped>
.listen-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  font-size: 14px;
  font-weight: 500;
  color: white;
  background: var(--td-green);
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.2s;
}

.listen-btn:hover {
  background: #006B31;
}

.listen-icon {
  font-size: 16px;
}

.btn-sm {
  padding: 4px 10px;
  font-size: 12px;
  font-weight: 500;
  color: var(--td-gray-700);
  background: white;
  border: 1px solid var(--td-gray-300);
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.15s;
}

.btn-sm:hover {
  background: var(--td-gray-50);
  border-color: var(--td-gray-400);
}

.transcript-body {
  padding: 0 !important;
}

.transcript-container {
  max-height: 400px;
  overflow-y: auto;
}

.transcript-line {
  padding: 12px 16px;
  border-bottom: 1px solid var(--td-gray-100);
}

.transcript-line:last-child {
  border-bottom: none;
}

.transcript-speaker {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 6px;
}

.transcript-speaker.agent .speaker-label {
  color: var(--td-green);
  font-weight: 600;
}

.transcript-speaker.customer .speaker-label {
  color: #2563EB;
  font-weight: 600;
}

.speaker-label {
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.transcript-time {
  font-size: 11px;
  color: var(--td-gray-400);
}

.transcript-text {
  font-size: 14px;
  line-height: 1.6;
  color: var(--td-gray-800);
  padding-left: 0;
}

.transcript-line:nth-child(odd) {
  background: var(--td-gray-50);
}
</style>
