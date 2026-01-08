<template>
  <div class="analysis-section">
    <div class="analysis-header">
      <h2 class="analysis-title">Analysis</h2>
    </div>

    <!-- Tier Order Selector -->
    <div class="tier-selector">
      <span class="tier-label">Hierarchy Order:</span>
      <div class="tier-dropdowns">
        <div v-for="(tier, index) in tierOrder" :key="index" class="tier-select-wrapper">
          <span class="tier-number">{{ index + 1 }}</span>
          <select
            :value="tier"
            @change="updateTierOrder(index, $event.target.value)"
            class="tier-select"
          >
            <option
              v-for="option in getAvailableOptions(index)"
              :key="option"
              :value="option"
            >
              {{ tierLabels[option] }}
            </option>
          </select>
          <span v-if="index < tierOrder.length - 1" class="tier-arrow">→</span>
        </div>
      </div>
    </div>

    <div class="analysis-layout">
      <!-- Left Sidebar: Taxonomy Tree -->
      <div class="analysis-sidebar">
        <TaxonomyTree
          :tree-data="taxonomyData"
          :selected-path="selectedPath"
          :tier-config="tierConfig"
          @select="handleTreeSelect"
        />
      </div>

      <!-- Right Content: Tabbed Panels -->
      <div class="analysis-content">
        <div class="analysis-tabs">
          <button
            v-for="tab in enabledTabs"
            :key="tab.key"
            :class="['tab-btn', { active: activeTab === tab.key }]"
            @click="activeTab = tab.key"
          >
            {{ tab.label }}
          </button>
        </div>

        <div class="tab-content">
          <TrendsPanel
            v-if="activeTab === 'trends'"
            :filters="effectiveFilters"
          />
          <SegmentsPanel
            v-if="activeTab === 'segments'"
            :filters="effectiveFilters"
          />
          <ProductsPanel
            v-if="activeTab === 'products'"
            :filters="effectiveFilters"
            @select-product="handleProductSelect"
          />
          <RootCausesPanel
            v-if="activeTab === 'root_causes'"
            :filters="effectiveFilters"
          />
          <CallInteractionsPanel
            v-if="activeTab === 'interactions'"
            :filters="effectiveFilters"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import TaxonomyTree from './TaxonomyTree.vue'
import TrendsPanel from './analysis/TrendsPanel.vue'
import SegmentsPanel from './analysis/SegmentsPanel.vue'
import ProductsPanel from './analysis/ProductsPanel.vue'
import RootCausesPanel from './analysis/RootCausesPanel.vue'
import CallInteractionsPanel from './analysis/CallInteractionsPanel.vue'
import { getBreakdown } from '../services/api'

const props = defineProps({
  filters: {
    type: Object,
    default: () => ({})
  },
  tabs: {
    type: Array,
    default: () => ['trends', 'segments', 'products', 'root_causes', 'interactions']
  }
})

const emit = defineEmits(['filter-change'])

const activeTab = ref('trends')
const taxonomyData = ref([])
const selectedPath = ref({})
const loadingTaxonomy = ref(false)

// Available tiers and their labels
const availableTiers = ['line_of_business', 'call_reason', 'product', 'region']
const tierLabels = {
  line_of_business: 'Line of Business',
  call_reason: 'Call Reason',
  product: 'Product',
  region: 'Region'
}

// Map tier keys to filter keys
const tierToFilterKey = {
  line_of_business: 'lineOfBusiness',
  call_reason: 'callReason',
  product: 'product',
  region: 'region'
}

// Current tier order (user-configurable, no duplicates)
const tierOrder = ref(['line_of_business', 'call_reason', 'product', 'region'])

// Tier config for TaxonomyTree - computed from tierOrder
const tierConfig = computed(() => {
  return tierOrder.value.map((tier, index) => ({
    key: tier,
    label: tierLabels[tier],
    level: index + 1,
    filterKey: tierToFilterKey[tier]
  }))
})

// Get available options for a tier dropdown (excluding already selected tiers before this index)
function getAvailableOptions(tierIndex) {
  const selectedBefore = tierOrder.value.slice(0, tierIndex)
  // Current selection should also be available
  const currentSelection = tierOrder.value[tierIndex]
  return availableTiers.filter(t => !selectedBefore.includes(t) || t === currentSelection)
}

// Update tier order when user changes a dropdown
function updateTierOrder(index, newValue) {
  const newOrder = [...tierOrder.value]
  const oldValue = newOrder[index]

  // Find if the newValue exists elsewhere in the array (after this index)
  const existingIndex = newOrder.findIndex((t, i) => i > index && t === newValue)

  if (existingIndex !== -1) {
    // Swap the values
    newOrder[existingIndex] = oldValue
  }

  newOrder[index] = newValue
  tierOrder.value = newOrder

  // Clear selections and reload taxonomy
  selectedPath.value = {}
  loadTaxonomyData()
}

const tabConfig = {
  trends: { key: 'trends', label: 'Trends' },
  segments: { key: 'segments', label: 'Segments' },
  products: { key: 'products', label: 'Products' },
  root_causes: { key: 'root_causes', label: 'Root Causes' },
  interactions: { key: 'interactions', label: 'Call Interactions' }
}

const enabledTabs = computed(() => {
  return props.tabs.map(t => tabConfig[t]).filter(Boolean)
})

// Effective filters = base filters + tree selection (using dynamic tier keys)
const effectiveFilters = computed(() => {
  const filters = { ...props.filters }

  // Apply selections from the tree based on tier config
  tierConfig.value.forEach(tier => {
    if (selectedPath.value[tier.key]) {
      filters[tier.filterKey] = selectedPath.value[tier.key]
    }
  })

  return filters
})

async function loadTaxonomyData() {
  loadingTaxonomy.value = true
  try {
    // Build tree based on current tier order
    const treeData = await buildTierLevel(props.filters, 0)
    taxonomyData.value = treeData
  } catch (error) {
    console.error('Failed to load taxonomy:', error)
    taxonomyData.value = []
  } finally {
    loadingTaxonomy.value = false
  }
}

// Recursively build taxonomy tree based on tier order
async function buildTierLevel(filters, levelIndex, maxDepth = 4) {
  if (levelIndex >= tierOrder.value.length || levelIndex >= maxDepth) {
    return null
  }

  const tierKey = tierOrder.value[levelIndex]
  const result = await getBreakdown(filters, tierKey)

  // Limit items per level based on depth
  const limit = levelIndex === 0 ? 6 : (levelIndex === 1 ? 5 : 4)
  const items = result.data.slice(0, limit)

  const nodes = []
  for (const item of items) {
    const node = {
      label: item.label,
      count: item.count,
      tierKey: tierKey,
      children: null
    }

    // Only load children for first 3 levels
    if (levelIndex < 3) {
      const childFilters = { ...filters }
      childFilters[tierToFilterKey[tierKey]] = item.label
      node.children = await buildTierLevel(childFilters, levelIndex + 1, maxDepth)
    }

    nodes.push(node)
  }

  return nodes
}

function handleTreeSelect(event) {
  selectedPath.value = event.path
  emit('filter-change', effectiveFilters.value)
}

function handleProductSelect(productLabel) {
  // Find the product tier key if it exists
  const productTier = tierConfig.value.find(t => t.key === 'product')
  if (productTier) {
    selectedPath.value = {
      ...selectedPath.value,
      product: productLabel
    }
  }
  emit('filter-change', effectiveFilters.value)
}

// Set default active tab to first enabled
watch(() => props.tabs, (newTabs) => {
  if (newTabs.length && !newTabs.includes(activeTab.value)) {
    activeTab.value = newTabs[0]
  }
}, { immediate: true })

onMounted(() => {
  loadTaxonomyData()
})
</script>

<style scoped>
.analysis-section {
  background: white;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  margin-top: 24px;
}

.analysis-header {
  padding: 16px 20px;
  border-bottom: 1px solid var(--td-gray-200);
  background: var(--td-gray-50);
}

.analysis-title {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: var(--td-gray-900);
}

/* Tier Selector Styles */
.tier-selector {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 20px;
  background: var(--td-gray-50);
  border-bottom: 1px solid var(--td-gray-200);
  flex-wrap: wrap;
}

.tier-label {
  font-size: 12px;
  font-weight: 600;
  color: var(--td-gray-600);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.tier-dropdowns {
  display: flex;
  align-items: center;
  gap: 4px;
  flex-wrap: wrap;
}

.tier-select-wrapper {
  display: flex;
  align-items: center;
  gap: 4px;
}

.tier-number {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 18px;
  height: 18px;
  font-size: 10px;
  font-weight: 600;
  color: white;
  background: var(--td-green);
  border-radius: 50%;
}

.tier-select {
  padding: 4px 8px;
  font-size: 12px;
  border: 1px solid var(--td-gray-300);
  border-radius: 4px;
  background: white;
  color: var(--td-gray-800);
  cursor: pointer;
  min-width: 110px;
}

.tier-select:hover {
  border-color: var(--td-gray-400);
}

.tier-select:focus {
  outline: none;
  border-color: var(--td-green);
  box-shadow: 0 0 0 2px rgba(0, 132, 61, 0.1);
}

.tier-arrow {
  font-size: 14px;
  color: var(--td-gray-400);
  margin: 0 4px;
}

.analysis-layout {
  display: flex;
  min-height: 500px;
}

.analysis-sidebar {
  width: 280px;
  border-right: 1px solid var(--td-gray-200);
  flex-shrink: 0;
}

.analysis-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.analysis-tabs {
  display: flex;
  border-bottom: 1px solid var(--td-gray-200);
  background: var(--td-gray-50);
}

.tab-btn {
  padding: 12px 20px;
  font-size: 13px;
  font-weight: 500;
  color: var(--td-gray-600);
  background: transparent;
  border: none;
  border-bottom: 2px solid transparent;
  cursor: pointer;
  transition: all 0.2s;
}

.tab-btn:hover {
  color: var(--td-gray-900);
  background: var(--td-gray-100);
}

.tab-btn.active {
  color: var(--td-green);
  border-bottom-color: var(--td-green);
  background: white;
}

.tab-content {
  flex: 1;
  overflow: auto;
}

/* Responsive */
@media (max-width: 900px) {
  .analysis-layout {
    flex-direction: column;
  }

  .analysis-sidebar {
    width: 100%;
    border-right: none;
    border-bottom: 1px solid var(--td-gray-200);
  }
}
</style>
