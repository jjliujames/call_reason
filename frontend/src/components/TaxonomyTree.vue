<template>
  <div class="taxonomy-tree">
    <div class="tree-header">
      <span class="tree-title">Filter by Taxonomy</span>
      <button v-if="hasSelection" class="clear-btn" @click="clearSelection">Clear</button>
    </div>

    <div class="tree-content">
      <!-- Level 1 nodes -->
      <div v-for="node1 in treeData" :key="node1.label" class="tree-node">
        <div
          :class="['tree-item', 'level-1', { selected: isSelected(0, node1.label), expanded: expanded[node1.label] }]"
          @click="handleNodeClick(node1, 0, [])"
        >
          <span class="expand-icon">{{ hasChildren(node1) ? (expanded[node1.label] ? '▼' : '▶') : '○' }}</span>
          <span class="node-label">{{ node1.label }}</span>
          <span class="node-count">{{ node1.count?.toLocaleString() || '0' }}</span>
        </div>

        <!-- Level 2 nodes -->
        <div v-if="expanded[node1.label] && hasChildren(node1)" class="tree-children">
          <div v-for="node2 in node1.children" :key="node2.label" class="tree-node">
            <div
              :class="['tree-item', 'level-2', { selected: isSelected(1, node2.label), expanded: expanded[getKey(node1, node2)] }]"
              @click.stop="handleNodeClick(node2, 1, [node1])"
            >
              <span class="expand-icon">{{ hasChildren(node2) ? (expanded[getKey(node1, node2)] ? '▼' : '▶') : '○' }}</span>
              <span class="node-label">{{ node2.label }}</span>
              <span class="node-count">{{ node2.count?.toLocaleString() || '0' }}</span>
            </div>

            <!-- Level 3 nodes -->
            <div v-if="expanded[getKey(node1, node2)] && hasChildren(node2)" class="tree-children">
              <div v-for="node3 in node2.children" :key="node3.label" class="tree-node">
                <div
                  :class="['tree-item', 'level-3', { selected: isSelected(2, node3.label), expanded: expanded[getKey(node1, node2, node3)] }]"
                  @click.stop="handleNodeClick(node3, 2, [node1, node2])"
                >
                  <span class="expand-icon">{{ hasChildren(node3) ? (expanded[getKey(node1, node2, node3)] ? '▼' : '▶') : '●' }}</span>
                  <span class="node-label">{{ node3.label }}</span>
                  <span class="node-count">{{ node3.count?.toLocaleString() || '0' }}</span>
                </div>

                <!-- Level 4 nodes -->
                <div v-if="expanded[getKey(node1, node2, node3)] && hasChildren(node3)" class="tree-children">
                  <div v-for="node4 in node3.children" :key="node4.label" class="tree-node">
                    <div
                      :class="['tree-item', 'level-4', { selected: isSelected(3, node4.label) }]"
                      @click.stop="handleNodeClick(node4, 3, [node1, node2, node3])"
                    >
                      <span class="leaf-icon">●</span>
                      <span class="node-label">{{ node4.label }}</span>
                      <span class="node-count">{{ node4.count?.toLocaleString() || '0' }}</span>
                    </div>
                  </div>
                </div>
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
  },
  selectedPath: {
    type: Object,
    default: () => ({})
  },
  tierConfig: {
    type: Array,
    default: () => [
      { key: 'line_of_business', label: 'Line of Business', level: 1 },
      { key: 'call_reason', label: 'Call Reason', level: 2 },
      { key: 'product', label: 'Product', level: 3 },
      { key: 'region', label: 'Region', level: 4 }
    ]
  }
})

const emit = defineEmits(['select'])

const expanded = ref({})

const hasSelection = computed(() => {
  return Object.values(props.selectedPath).some(v => v !== null && v !== undefined)
})

function hasChildren(node) {
  return node.children && node.children.length > 0
}

function getKey(...nodes) {
  return nodes.map(n => n.label).join('/')
}

function isSelected(levelIndex, label) {
  const tierKey = props.tierConfig[levelIndex]?.key
  return tierKey && props.selectedPath[tierKey] === label
}

function handleNodeClick(node, levelIndex, path) {
  const nodeKey = [...path.map(p => p.label), node.label].join('/')

  // Toggle expansion if node has children
  if (hasChildren(node)) {
    expanded.value[nodeKey] = !expanded.value[nodeKey]
  }

  // Ensure parent nodes are expanded
  let pathKey = ''
  path.forEach(item => {
    pathKey = pathKey ? `${pathKey}/${item.label}` : item.label
    expanded.value[pathKey] = true
  })

  // Build selection path
  const newPath = {}
  path.forEach((item, index) => {
    const tierKey = props.tierConfig[index]?.key
    if (tierKey) {
      newPath[tierKey] = item.label
    }
  })

  // Add current node to selection
  const nodeTierKey = node.tierKey || props.tierConfig[levelIndex]?.key
  if (nodeTierKey) {
    newPath[nodeTierKey] = node.label
  }

  emit('select', { level: nodeTierKey, value: node.label, path: newPath })
}

function clearSelection() {
  emit('select', { level: null, value: null, path: {} })
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

.tree-node {
  /* Container for node and its children */
  display: block;
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

.tree-item.level-4 {
  padding-left: 68px;
  font-weight: 400;
  color: var(--td-gray-600);
}

.expand-icon {
  font-size: 10px;
  color: var(--td-gray-500);
  width: 12px;
  text-align: center;
  flex-shrink: 0;
}

.leaf-icon {
  font-size: 6px;
  color: var(--td-gray-400);
  width: 12px;
  text-align: center;
  flex-shrink: 0;
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
  flex-shrink: 0;
}

.tree-children {
  /* Children container */
  display: block;
}
</style>
