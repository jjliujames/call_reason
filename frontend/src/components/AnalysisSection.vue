<template>
  <div class="analysis-section">
    <div class="analysis-header">
      <h2 class="analysis-title">Analysis</h2>
    </div>

    <div class="analysis-layout">
      <!-- Left Sidebar: Taxonomy Tree -->
      <div class="analysis-sidebar">
        <TaxonomyTree
          :tree-data="taxonomyData"
          :selected-path="selectedPath"
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
import { getBreakdown } from '../services/api'

const props = defineProps({
  filters: {
    type: Object,
    default: () => ({})
  },
  tabs: {
    type: Array,
    default: () => ['trends', 'segments', 'products', 'root_causes']
  }
})

const emit = defineEmits(['filter-change'])

const activeTab = ref('trends')
const taxonomyData = ref([])
const selectedPath = ref({ lob: null, callReason: null, product: null })
const loadingTaxonomy = ref(false)

const tabConfig = {
  trends: { key: 'trends', label: 'Trends' },
  segments: { key: 'segments', label: 'Segments' },
  products: { key: 'products', label: 'Products' },
  root_causes: { key: 'root_causes', label: 'Root Causes' }
}

const enabledTabs = computed(() => {
  return props.tabs.map(t => tabConfig[t]).filter(Boolean)
})

// Effective filters = base filters + tree selection
const effectiveFilters = computed(() => {
  return {
    ...props.filters,
    lineOfBusiness: selectedPath.value.lob || props.filters.lineOfBusiness,
    callReason: selectedPath.value.callReason || props.filters.callReason,
    product: selectedPath.value.product || props.filters.product
  }
})

async function loadTaxonomyData() {
  loadingTaxonomy.value = true
  try {
    // Load LOB breakdown
    const lobResult = await getBreakdown(props.filters, 'line_of_business')
    const lobData = lobResult.data

    // For each LOB, load call reasons
    const treeData = []
    for (const lob of lobData.slice(0, 6)) {
      const lobFilters = { ...props.filters, lineOfBusiness: lob.label }
      const reasonResult = await getBreakdown(lobFilters, 'call_reason')

      const lobNode = {
        label: lob.label,
        count: lob.count,
        children: []
      }

      // For each call reason, load products
      for (const reason of reasonResult.data.slice(0, 5)) {
        const reasonFilters = { ...lobFilters, callReason: reason.label }
        const productResult = await getBreakdown(reasonFilters, 'product')

        lobNode.children.push({
          label: reason.label,
          count: reason.count,
          children: productResult.data.slice(0, 5).map(p => ({
            label: p.label,
            count: p.count
          }))
        })
      }

      treeData.push(lobNode)
    }

    taxonomyData.value = treeData
  } catch (error) {
    console.error('Failed to load taxonomy:', error)
    taxonomyData.value = []
  } finally {
    loadingTaxonomy.value = false
  }
}

function handleTreeSelect(event) {
  selectedPath.value = event.path
  emit('filter-change', effectiveFilters.value)
}

function handleProductSelect(productLabel) {
  selectedPath.value = {
    ...selectedPath.value,
    product: productLabel
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
