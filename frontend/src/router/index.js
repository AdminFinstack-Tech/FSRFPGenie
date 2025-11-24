import { createRouter, createWebHistory } from 'vue-router'
import Dashboard from '../views/DashboardProfessional.vue'
import Upload from '../views/UploadProfessional.vue'
import Search from '../views/SearchProfessional.vue'
import Documents from '../views/DocumentsProfessional.vue'
import Templates from '../views/TemplatesProfessional.vue'
import ColumnMapping from '../views/ColumnMapping.vue'

const routes = [
  {
    path: '/',
    name: 'Dashboard',
    component: Dashboard
  },
  {
    path: '/upload',
    name: 'Upload',
    component: Upload
  },
  {
    path: '/search',
    name: 'Search',
    component: Search
  },
  {
    path: '/documents',
    name: 'Documents',
    component: Documents
  },
  {
    path: '/templates',
    name: 'Templates',
    component: Templates
  },
  {
    path: '/mapping/:documentId',
    name: 'ColumnMapping',
    component: ColumnMapping,
    props: true
  }
]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
})

export default router