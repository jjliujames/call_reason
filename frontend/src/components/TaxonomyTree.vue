<template>
  <div class="taxonomy-tree">
    <div class="tree-header">
      <span class="tree-title">Filter by Taxonomy</span>
      <button v-if="hasSelection" class="clear-btn" @click="clearSelection">Clear</button>
    </div>

    <div class="tree-content">
      <!-- Level 1: Lines of Business -->
      <div v-for="lob in treeData" :key="lob.label" class="tree-node">
        <div
          :class="['tree-item', 'level-1', { selected: isSelected('lob', lob.label), expanded: expanded[lob.label] }]"
          @click="toggleExpand(lob.label)"
        >
          <span class="expand-icon">{{ expanded[lob.label] ? '▼' : '▶' }}</span>
          <span class="node-label">{{ lob.label }}</span>
          <span class="node-count">{{ lob.count.toLocaleString() }}</span>
        </div>

        <!-- Level 2: Call Reasons -->
        <div v-if="expanded[lob.label]" class="tree-children">
          <div v-for="reason in lob.children" :key="reason.label" class="tree-node">
            <div
              :class="['tree-item', 'level-2', { selected: isSelected('callReason', reason.label), expanded: expanded[`${lob.label}/${reason.label}`] }]"
              @click.stop="toggleExpandReason(lob.label, reason.label)"
            >
              <span class="expand-icon">{{ reason.children?.length ? (expanded[`${lob.label}/${reason.label}`] ? '▼' : '▶') : '○' }}</span>
              <span class="node-label">{{ reason.label }}</span>
              <span class="node-count">{{ reason.count.toLocaleString() }}</span>
            </div>

            <!-- Level 3: Products -->
            <div v-if="expanded[`${lob.label}/${reason.label}`] && reason.children?.length" class="tree-children">
              <div
                v-for="product in reason.children"
                :key="product.label"
                :class="['tree-item', 'level-3', { selected: isSelected('product', product.label) }]"
                @click.stop="selectProduct(lob.label, reason.label, product.label)"
              >
                <span class="leaf-icon">●</span>
                <span class="node-label">{{ product.label }}</span>
                <span class="node-count">{{ product.count.toLocaleString() }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  treeData: {
    type: Array,
    required: true
    // Structure: [{ label, count, children: [{ label, count, children: [...] }] }]
  },
  selectedPath: {
    type: Object,
    default: () => ({ lob: null, callReason: null, product: null })
  }
})

const emit = defineEmits(['select'])

const expanded = ref({})

const hasSelection = computed(() => {
  return props.selectedPath.lob || props.selectedPath.callReason || props.selectedPath.product
})

function isSelected(level, value) {
  return props.selectedPath[level] === value
}

function toggleExpand(lobLabel) {
  expanded.value[lobLabel] = !expanded.value[lobLabel]
  // Select this LOB when expanding
  emit('select', { level: 'lob', value: lobLabel, path: { lob: lobLabel, callReason: null, product: null } })
}

function toggleExpandReason(lobLabel, reasonLabel) {
  const key = `${lobLabel}/${reasonLabel}`
  expanded.value[key] = !expanded.value[key]
  // Ensure parent is expanded
  expanded.value[lobLabel] = true
  // Select this call reason
  emit('select', { level: 'callReason', value: reasonLabel, path: { lob: lobLabel, callReason: reasonLabel, product: null } })
}

function selectProduct(lobLabel, reasonLabel, productLabel) {
  // Ensure parents are expanded
  expanded.value[lobLabel] = true
  expanded.value[`${lobLabel}/${reasonLabel}`] = true
  // Select this product
  emit('select', { level: 'product', value: productLabel, path: { lob: lobLabel, callReason: reasonLabel, product: productLabel } })
}

function clearSelection() {
  emit('select', { level: null, value: null, path: { lob: null, callReason: null, product: null } })
}
</script>

<style scoped>
.taxonomy-tree {
  background: white;
  border-radius: 8px;
  border: 1px solid var(--td-gray-200);
  overflow: hidden;
}

.tree-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: var(--td-gray-50);
  border-bottom: 1px solid var(--td-gray-200);
}

.tree-title {
  font-size: 12px;
  font-weight: 600;
  color: var(--td-gray-700);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.clear-btn {
  padding: 4px 8px;
  font-size: 11px;
  background: white;
  border: 1px solid var(--td-gray-300);
  border-radius: 4px;
  color: var(--td-gray-600);
  cursor: pointer;
}

.clear-btn:hover {
  background: var(--td-gray-100);
}

.tree-content {
  max-height: 400px;
  overflow-y: auto;
  padding: 8px 0;
}

.tree-item {
  display: flex;
  align-items: center;
  padding: 8px 12px;
  cursor: pointer;
  transition: background 0.15s;
  gap: 8px;
}

.tree-item:hover {
  background: var(--td-gray-50);
}

.tree-item.selected {
  background: #E6F4EA;
  border-left: 3px solid var(--td-green);
}

.tree-item.level-1 {
  font-weight: 600;
  color: var(--td-gray-900);
}

.tree-item.level-2 {
  padding-left: 28px;
  font-weight: 500;
  color: var(--td-gray-800);
}

.tree-item.level-3 {
  padding-left: 48px;
  font-weight: 400;
  color: var(--td-gray-700);
}

.expand-icon {
  font-size: 10px;
  color: var(--td-gray-500);
  width: 12px;
  text-align: center;
}

.leaf-icon {
  font-size: 6px;
  color: var(--td-gray-400);
  width: 12px;
  text-align: center;
}

.node-label {
  flex: 1;
  font-size: 13px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.node-count {
  font-size: 11px;
  color: var(--td-gray-500);
  background: var(--td-gray-100);
  padding: 2px 6px;
  border-radius: 10px;
  font-weight: 500;
}

.tree-children {
  /* Indent children */
}
</style>
