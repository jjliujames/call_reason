import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 30000
})

// Options / Taxonomy
export async function getOptions() {
  const response = await api.get('/options')
  return response.data
}

// Interactions
export async function getInteractions(filters = {}, page = 1, pageSize = 50) {
  const params = {
    page,
    page_size: pageSize,
    sort_by: 'timestamp',
    sort_order: 'desc'
  }

  if (filters.from) params.from = filters.from
  if (filters.to) params.to = filters.to
  if (filters.lineOfBusiness) params.lob = filters.lineOfBusiness
  if (filters.callReason) params.call_reason = filters.callReason
  if (filters.product) params.product = filters.product
  if (filters.region) params.region = filters.region
  if (filters.teamLeader) params.team_leader = filters.teamLeader
  if (filters.agentId) params.agent_id = filters.agentId
  if (filters.complaintsOnly) params.complaints_only = true
  if (filters.channel) params.channel = filters.channel
  if (filters.segment) params.segment = filters.segment

  const response = await api.get('/interactions', { params })
  return response.data
}

export async function getInteractionById(id) {
  const response = await api.get(`/interactions/${id}`)
  return response.data
}

export async function getRelatedInteractions(id, mode = 'same_reason_product', limit = 20) {
  const response = await api.get(`/interactions/${id}/related`, {
    params: { mode, limit }
  })
  return response.data
}

// Root Cause Analysis
export async function analyzeRootCauses(data) {
  const response = await api.post('/root_cause', data)
  return response.data
}

// Metrics / Aggregations
export async function getMetrics(filters = {}) {
  const params = {}

  if (filters.from) params.from = filters.from
  if (filters.to) params.to = filters.to
  if (filters.lineOfBusiness) params.lob = filters.lineOfBusiness
  if (filters.callReason) params.call_reason = filters.callReason
  if (filters.product) params.product = filters.product
  if (filters.region) params.region = filters.region
  if (filters.teamLeader) params.team_leader = filters.teamLeader
  if (filters.agentId) params.agent_id = filters.agentId
  if (filters.complaintsOnly) params.complaints_only = true

  const response = await api.get('/metrics', { params })
  return response.data
}

export async function getTrends(filters = {}, aggregation = 'daily') {
  const params = { aggregation }

  if (filters.from) params.from = filters.from
  if (filters.to) params.to = filters.to
  if (filters.lineOfBusiness) params.lob = filters.lineOfBusiness
  if (filters.callReason) params.call_reason = filters.callReason
  if (filters.product) params.product = filters.product
  if (filters.region) params.region = filters.region
  if (filters.complaintsOnly) params.complaints_only = true

  const response = await api.get('/trends', { params })
  return response.data
}

export async function getBreakdown(filters = {}, groupBy = 'line_of_business') {
  const params = { group_by: groupBy }

  if (filters.from) params.from = filters.from
  if (filters.to) params.to = filters.to
  if (filters.lineOfBusiness) params.lob = filters.lineOfBusiness
  if (filters.callReason) params.call_reason = filters.callReason
  if (filters.product) params.product = filters.product
  if (filters.region) params.region = filters.region
  if (filters.complaintsOnly) params.complaints_only = true

  const response = await api.get('/breakdown', { params })
  return response.data
}

export async function getAgentPerformance(filters = {}) {
  const params = {}

  if (filters.from) params.from = filters.from
  if (filters.to) params.to = filters.to
  if (filters.region) params.region = filters.region
  if (filters.teamLeader) params.team_leader = filters.teamLeader

  const response = await api.get('/agents/performance', { params })
  return response.data
}

// Metrics Comparison (Week-over-Week)
export async function getMetricsComparison(currentFrom, currentTo, filters = {}, previousFrom = null, previousTo = null) {
  const params = {
    currentFrom,
    currentTo
  }

  if (previousFrom) params.previousFrom = previousFrom
  if (previousTo) params.previousTo = previousTo
  if (filters.lineOfBusiness) params.lob = filters.lineOfBusiness
  if (filters.callReason) params.call_reason = filters.callReason
  if (filters.product) params.product = filters.product
  if (filters.region) params.region = filters.region
  if (filters.complaintsOnly) params.complaints_only = true

  const response = await api.get('/metrics/comparison', { params })
  return response.data
}

// Severity Breakdown
export async function getSeverityBreakdown(filters = {}) {
  const params = {}

  if (filters.from) params.from = filters.from
  if (filters.to) params.to = filters.to
  if (filters.lineOfBusiness) params.lob = filters.lineOfBusiness
  if (filters.callReason) params.call_reason = filters.callReason
  if (filters.product) params.product = filters.product
  if (filters.region) params.region = filters.region

  const response = await api.get('/metrics/severity-breakdown', { params })
  return response.data
}

// Complaint Heatmap
export async function getComplaintHeatmap(filters = {}) {
  const params = {}

  if (filters.from) params.from = filters.from
  if (filters.to) params.to = filters.to
  if (filters.lineOfBusiness) params.lob = filters.lineOfBusiness
  if (filters.region) params.region = filters.region

  const response = await api.get('/metrics/heatmap', { params })
  return response.data
}

// Agent Profile (Coaching)
export async function getAgentProfile(agentId, filters = {}) {
  const params = {}

  if (filters.from) params.from = filters.from
  if (filters.to) params.to = filters.to

  const response = await api.get(`/agents/${agentId}/profile`, { params })
  return response.data
}

export default api
