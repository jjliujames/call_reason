import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      redirect: '/interactions'
    },
    {
      path: '/interactions',
      name: 'interactions',
      component: () => import('../views/InteractionsList.vue'),
      meta: { title: 'Interactions' }
    },
    {
      path: '/interactions/:id',
      name: 'interaction-detail',
      component: () => import('../views/InteractionDetail.vue'),
      meta: { title: 'Interaction Detail' }
    },
    {
      path: '/call-reasons',
      name: 'call-reasons',
      component: () => import('../views/CallReasonView.vue'),
      meta: { title: 'Call Reason Analysis' }
    },
    {
      path: '/complaints',
      name: 'complaints',
      component: () => import('../views/ComplaintsView.vue'),
      meta: { title: 'Complaints Analysis' }
    },
    {
      path: '/agents',
      name: 'agents',
      component: () => import('../views/AgentsView.vue'),
      meta: { title: 'Agent Performance' }
    },
    {
      path: '/root-cause',
      name: 'root-cause',
      component: () => import('../views/RootCauseView.vue'),
      meta: { title: 'Root Cause Analysis' }
    },
    {
      path: '/actions',
      name: 'actions',
      component: () => import('../views/ActionsView.vue'),
      meta: { title: 'Actions & Opportunities' }
    }
  ]
})

export default router
