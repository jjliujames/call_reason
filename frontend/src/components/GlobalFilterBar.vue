<template>
  <div class="filter-bar">
    <div class="filter-group">
      <label>Date Range</label>
      <select v-model="dateRange" @change="handleDateRangeChange">
        <option value="7">Last 7 Days</option>
        <option value="30">Last 30 Days</option>
        <option value="60">Last 60 Days</option>
        <option value="90">Last 90 Days</option>
      </select>
    </div>

    <div class="filter-group" v-if="showFilters.includes('lob')">
      <label>Line of Business</label>
      <select v-model="localFilters.lineOfBusiness" @change="emitChange">
        <option value="">All Lines</option>
        <option v-for="lob in options.linesOfBusiness" :key="lob" :value="lob">{{ lob }}</option>
      </select>
    </div>

    <div class="filter-group" v-if="showFilters.includes('callReason')">
      <label>Call Reason</label>
      <select v-model="localFilters.callReason" @change="emitChange">
        <option value="">All Reasons</option>
        <option v-for="reason in options.callReasons" :key="reason" :value="reason">{{ reason }}</option>
      </select>
    </div>

    <div class="filter-group" v-if="showFilters.includes('product')">
      <label>Product</label>
      <select v-model="localFilters.product" @change="emitChange">
        <option value="">All Products</option>
        <option v-for="product in options.products" :key="product" :value="product">{{ product }}</option>
      </select>
    </div>

    <div class="filter-group" v-if="showFilters.includes('region')">
      <label>Region</label>
      <select v-model="localFilters.region" @change="emitChange">
        <option value="">All Regions</option>
        <option v-for="region in options.regions" :key="region" :value="region">{{ region }}</option>
      </select>
    </div>

    <div class="filter-group" v-if="showFilters.includes('complaintsOnly')">
      <label>&nbsp;</label>
      <label style="display: flex; align-items: center; gap: 8px; cursor: pointer;">
        <input type="checkbox" v-model="localFilters.complaintsOnly" @change="emitChange" />
        <span style="font-size: 13px; text-transform: none;">Complaints Only</span>
      </label>
    </div>

    <div class="filter-group" v-if="store.hasActiveFilters">
      <label>&nbsp;</label>
      <button class="btn btn-secondary btn-sm" @click="resetFilters">Reset Filters</button>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, watch, onMounted } from 'vue'
import { useMainStore } from '../stores/main'

const props = defineProps({
  showFilters: {
    type: Array,
    default: () => ['lob', 'callReason', 'product', 'region', 'complaintsOnly']
  }
})

const emit = defineEmits(['change'])
const store = useMainStore()
const options = store.options

const dateRange = ref('30')

const localFilters = reactive({
  from: store.globalFilters.from,
  to: store.globalFilters.to,
  lineOfBusiness: store.globalFilters.lineOfBusiness,
  callReason: store.globalFilters.callReason,
  product: store.globalFilters.product,
  region: store.globalFilters.region,
  teamLeader: store.globalFilters.teamLeader,
  agentId: store.globalFilters.agentId,
  complaintsOnly: store.globalFilters.complaintsOnly
})

function calculateDateRange(days) {
  const to = new Date()
  const from = new Date()
  from.setDate(from.getDate() - days)
  return {
    from: from.toISOString().split('T')[0],
    to: to.toISOString().split('T')[0]
  }
}

function handleDateRangeChange() {
  const { from, to } = calculateDateRange(parseInt(dateRange.value))
  localFilters.from = from
  localFilters.to = to
  emitChange()
}

function emitChange() {
  store.setGlobalFilters({ ...localFilters })
  emit('change', { ...localFilters })
}

function resetFilters() {
  dateRange.value = '30'
  const { from, to } = calculateDateRange(30)
  Object.assign(localFilters, {
    from,
    to,
    lineOfBusiness: '',
    callReason: '',
    product: '',
    region: '',
    teamLeader: '',
    agentId: '',
    complaintsOnly: false
  })
  emitChange()
}

// Sync with store when external changes happen
watch(() => store.globalFilters, (newFilters) => {
  Object.assign(localFilters, newFilters)
}, { deep: true })

onMounted(() => {
  handleDateRangeChange()
})
</script>
