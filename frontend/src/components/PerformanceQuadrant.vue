<template>
  <div class="performance-quadrant">
    <div class="quadrant-chart">
      <apexchart
        type="scatter"
        height="350"
        :options="chartOptions"
        :series="series"
      />
    </div>

    <div class="quadrant-summary">
      <div class="quadrant-box stars">
        <span class="quadrant-icon">★</span>
        <div class="quadrant-info">
          <span class="quadrant-label">Stars</span>
          <span class="quadrant-count">{{ counts.stars }}</span>
        </div>
        <span class="quadrant-desc">High FCR, Low Complaints</span>
      </div>

      <div class="quadrant-box coaches">
        <span class="quadrant-icon">🎯</span>
        <div class="quadrant-info">
          <span class="quadrant-label">Coaches</span>
          <span class="quadrant-count">{{ counts.coaches }}</span>
        </div>
        <span class="quadrant-desc">High FCR, High Complaints</span>
      </div>

      <div class="quadrant-box solid">
        <span class="quadrant-icon">✓</span>
        <div class="quadrant-info">
          <span class="quadrant-label">Solid</span>
          <span class="quadrant-count">{{ counts.solid }}</span>
        </div>
        <span class="quadrant-desc">Low FCR, Low Complaints</span>
      </div>

      <div class="quadrant-box at-risk">
        <span class="quadrant-icon">⚠</span>
        <div class="quadrant-info">
          <span class="quadrant-label">At Risk</span>
          <span class="quadrant-count">{{ counts.atRisk }}</span>
        </div>
        <span class="quadrant-desc">Low FCR, High Complaints</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  agents: { type: Array, default: () => [] },
  fcrThreshold: { type: Number, default: 75 },
  complaintThreshold: { type: Number, default: 25 }
})

const emit = defineEmits(['agent-click'])

// Classify agents into quadrants
const classifiedAgents = computed(() => {
  return props.agents.map(agent => {
    const fcr = agent.fcr_rate || 0
    const complaint = agent.complaint_rate || 0

    let quadrant
    if (fcr >= props.fcrThreshold && complaint <= props.complaintThreshold) {
      quadrant = 'stars'
    } else if (fcr >= props.fcrThreshold && complaint > props.complaintThreshold) {
      quadrant = 'coaches'
    } else if (fcr < props.fcrThreshold && complaint <= props.complaintThreshold) {
      quadrant = 'solid'
    } else {
      quadrant = 'atRisk'
    }

    return { ...agent, quadrant }
  })
})

const counts = computed(() => ({
  stars: classifiedAgents.value.filter(a => a.quadrant === 'stars').length,
  coaches: classifiedAgents.value.filter(a => a.quadrant === 'coaches').length,
  solid: classifiedAgents.value.filter(a => a.quadrant === 'solid').length,
  atRisk: classifiedAgents.value.filter(a => a.quadrant === 'atRisk').length
}))

const series = computed(() => {
  const quadrantColors = {
    stars: '#10B981',
    coaches: '#3B82F6',
    solid: '#6B7280',
    atRisk: '#EF4444'
  }

  const groups = {
    stars: [],
    coaches: [],
    solid: [],
    atRisk: []
  }

  for (const agent of classifiedAgents.value) {
    groups[agent.quadrant].push({
      x: agent.complaint_rate,
      y: agent.fcr_rate,
      agentId: agent.agent_id,
      agentName: agent.agent_name
    })
  }

  return [
    { name: 'Stars', data: groups.stars, color: quadrantColors.stars },
    { name: 'Coaches', data: groups.coaches, color: quadrantColors.coaches },
    { name: 'Solid', data: groups.solid, color: quadrantColors.solid },
    { name: 'At Risk', data: groups.atRisk, color: quadrantColors.atRisk }
  ]
})

const chartOptions = computed(() => ({
  chart: {
    toolbar: { show: false },
    zoom: { enabled: false },
    events: {
      dataPointSelection: (event, chartContext, config) => {
        const point = series.value[config.seriesIndex].data[config.dataPointIndex]
        if (point?.agentId) {
          emit('agent-click', point.agentId)
        }
      }
    }
  },
  colors: ['#10B981', '#3B82F6', '#6B7280', '#EF4444'],
  xaxis: {
    title: { text: 'Complaint Rate %', style: { fontSize: '12px' } },
    min: 0,
    max: Math.max(60, ...props.agents.map(a => a.complaint_rate || 0)),
    tickAmount: 6
  },
  yaxis: {
    title: { text: 'FCR Rate %', style: { fontSize: '12px' } },
    min: 40,
    max: 100,
    tickAmount: 6
  },
  annotations: {
    xaxis: [{
      x: props.complaintThreshold,
      borderColor: '#9CA3AF',
      strokeDashArray: 4,
      label: {
        text: `${props.complaintThreshold}% Complaint`,
        style: { fontSize: '10px', color: '#6B7280' }
      }
    }],
    yaxis: [{
      y: props.fcrThreshold,
      borderColor: '#9CA3AF',
      strokeDashArray: 4,
      label: {
        text: `${props.fcrThreshold}% FCR`,
        style: { fontSize: '10px', color: '#6B7280' }
      }
    }]
  },
  markers: {
    size: 8,
    hover: { size: 12 }
  },
  tooltip: {
    custom: ({ seriesIndex, dataPointIndex }) => {
      const point = series.value[seriesIndex].data[dataPointIndex]
      return `
        <div style="padding: 8px; font-size: 12px;">
          <strong>${point.agentName}</strong><br/>
          FCR: ${point.y}%<br/>
          Complaints: ${point.x}%
        </div>
      `
    }
  },
  legend: {
    position: 'top',
    horizontalAlign: 'right'
  },
  grid: {
    borderColor: '#E5E7EB'
  }
}))
</script>

<style scoped>
.performance-quadrant {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.quadrant-chart {
  min-height: 350px;
}

.quadrant-summary {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
}

.quadrant-box {
  padding: 12px;
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  text-align: center;
}

.quadrant-box.stars {
  background: rgba(16, 185, 129, 0.1);
  border: 1px solid rgba(16, 185, 129, 0.3);
}

.quadrant-box.coaches {
  background: rgba(59, 130, 246, 0.1);
  border: 1px solid rgba(59, 130, 246, 0.3);
}

.quadrant-box.solid {
  background: rgba(107, 114, 128, 0.1);
  border: 1px solid rgba(107, 114, 128, 0.3);
}

.quadrant-box.at-risk {
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.3);
}

.quadrant-icon {
  font-size: 20px;
}

.quadrant-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.quadrant-label {
  font-size: 13px;
  font-weight: 600;
  color: var(--td-gray-700);
}

.quadrant-count {
  font-size: 18px;
  font-weight: 700;
}

.quadrant-box.stars .quadrant-count { color: #10B981; }
.quadrant-box.coaches .quadrant-count { color: #3B82F6; }
.quadrant-box.solid .quadrant-count { color: #6B7280; }
.quadrant-box.at-risk .quadrant-count { color: #EF4444; }

.quadrant-desc {
  font-size: 10px;
  color: var(--td-gray-500);
}
</style>
