import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useMainStore = defineStore('main', () => {
  // Global Filters
  const globalFilters = ref({
    from: getDefaultFromDate(),
    to: getDefaultToDate(),
    lineOfBusiness: '',
    callReason: '',
    product: '',
    region: '',
    teamLeader: '',
    agentId: '',
    complaintsOnly: false,
    channel: '',
    segment: ''
  })

  // Navigation Context (breadcrumbs)
  const navigationContext = ref({
    breadcrumbs: []
  })

  // Last Root Cause Result
  const lastRootCauseResult = ref(null)

  // Options / Taxonomy
  const options = ref({
    linesOfBusiness: [],
    callReasons: [],
    products: [],
    regions: [],
    teamLeaders: {},
    allTeamLeaders: [],
    channels: [],
    customerSegments: [],
    tenureBands: [],
    complaintCategories: [],
    complaintSeverities: [],
    agents: []
  })

  // Actions
  function setOptions(data) {
    options.value = {
      linesOfBusiness: data.lines_of_business || [],
      callReasons: data.call_reasons || [],
      products: data.products || [],
      regions: data.regions || [],
      teamLeaders: data.team_leaders || {},
      allTeamLeaders: data.all_team_leaders || [],
      channels: data.channels || [],
      customerSegments: data.customer_segments || [],
      tenureBands: data.tenure_bands || [],
      complaintCategories: data.complaint_categories || [],
      complaintSeverities: data.complaint_severities || [],
      agents: data.agents || []
    }
  }

  function setGlobalFilters(filters) {
    globalFilters.value = { ...globalFilters.value, ...filters }
  }

  function resetFilters() {
    globalFilters.value = {
      from: getDefaultFromDate(),
      to: getDefaultToDate(),
      lineOfBusiness: '',
      callReason: '',
      product: '',
      region: '',
      teamLeader: '',
      agentId: '',
      complaintsOnly: false,
      channel: '',
      segment: ''
    }
  }

  function setBreadcrumbs(crumbs) {
    navigationContext.value.breadcrumbs = crumbs
  }

  function setLastRootCauseResult(result) {
    lastRootCauseResult.value = result
  }

  // Helper functions
  function getDefaultFromDate() {
    const date = new Date()
    date.setDate(date.getDate() - 30)
    return date.toISOString().split('T')[0]
  }

  function getDefaultToDate() {
    return new Date().toISOString().split('T')[0]
  }

  // Computed
  const hasActiveFilters = computed(() => {
    return !!(
      globalFilters.value.lineOfBusiness ||
      globalFilters.value.callReason ||
      globalFilters.value.product ||
      globalFilters.value.region ||
      globalFilters.value.teamLeader ||
      globalFilters.value.agentId ||
      globalFilters.value.complaintsOnly ||
      globalFilters.value.channel ||
      globalFilters.value.segment
    )
  })

  return {
    globalFilters,
    navigationContext,
    lastRootCauseResult,
    options,
    hasActiveFilters,
    setOptions,
    setGlobalFilters,
    resetFilters,
    setBreadcrumbs,
    setLastRootCauseResult
  }
})
