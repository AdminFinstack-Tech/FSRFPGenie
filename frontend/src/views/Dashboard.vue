<template>
  <div>
    <!-- Page Header with Actions -->
    <div class="d-flex justify-space-between align-center mb-6">
      <div>
        <h1 class="text-h3 font-weight-bold mb-2">Dashboard</h1>
        <p class="text-subtitle-1 text-grey-darken-1">Overview of your RFP knowledge base</p>
      </div>
      <v-btn color="primary" size="large" @click="$router.push('/upload')">
        <v-icon left>mdi-plus</v-icon>
        Upload Document
      </v-btn>
    </div>

    <!-- Stats Cards -->
    <v-row class="mb-6">
      <v-col cols="12" sm="6" md="3">
        <v-card class="pa-6 h-full" hover>
          <div class="d-flex align-center justify-space-between mb-2">
            <v-avatar color="blue-lighten-4" size="56" class="elevation-2">
              <v-icon color="blue-darken-2" size="32">mdi-file-document-multiple</v-icon>
            </v-avatar>
            <v-chip color="blue" variant="tonal" size="small">
              <v-icon left size="small">mdi-trending-up</v-icon>
              Active
            </v-chip>
          </div>
          <p class="text-h3 font-weight-bold mb-1">{{ stats.totalDocuments || 0 }}</p>
          <p class="text-subtitle-2 text-grey">Total Documents</p>
        </v-card>
      </v-col>

      <v-col cols="12" sm="6" md="3">
        <v-card class="pa-6 h-full" hover>
          <div class="d-flex align-center justify-space-between mb-2">
            <v-avatar color="green-lighten-4" size="56" class="elevation-2">
              <v-icon color="green-darken-2" size="32">mdi-database</v-icon>
            </v-avatar>
            <v-chip color="green" variant="tonal" size="small">
              <v-icon left size="small">mdi-check-circle</v-icon>
              Processed
            </v-chip>
          </div>
          <p class="text-h3 font-weight-bold mb-1">{{ stats.totalRecords || 0 }}</p>
          <p class="text-subtitle-2 text-grey">Total Records</p>
        </v-card>
      </v-col>

      <v-col cols="12" sm="6" md="3">
        <v-card class="pa-6 h-full" hover>
          <div class="d-flex align-center justify-space-between mb-2">
            <v-avatar color="purple-lighten-4" size="56" class="elevation-2">
              <v-icon color="purple-darken-2" size="32">mdi-package-variant</v-icon>
            </v-avatar>
            <v-chip color="purple" variant="tonal" size="small">
              {{ Object.keys(stats.productDistribution || {}).length }} types
            </v-chip>
          </div>
          <p class="text-h3 font-weight-bold mb-1">{{ getTotalProducts() }}</p>
          <p class="text-subtitle-2 text-grey">Product Items</p>
        </v-card>
      </v-col>

      <v-col cols="12" sm="6" md="3">
        <v-card class="pa-6 h-full" hover>
          <div class="d-flex align-center justify-space-between mb-2">
            <v-avatar color="orange-lighten-4" size="56" class="elevation-2">
              <v-icon color="orange-darken-2" size="32">mdi-clock-time-four</v-icon>
            </v-avatar>
            <v-chip color="orange" variant="tonal" size="small">
              Recent
            </v-chip>
          </div>
          <p class="text-h6 font-weight-bold mb-1">{{ formatDate(stats.lastUpload) }}</p>
          <p class="text-subtitle-2 text-grey">Last Upload</p>
        </v-card>
      </v-col>
    </v-row>

    <!-- Recent Documents & Product Distribution -->
    <v-row class="mb-6">
      <v-col cols="12" md="8">
        <v-card class="h-full">
          <v-card-title class="d-flex justify-space-between align-center">
            <div class="d-flex align-center">
              <v-icon left color="primary">mdi-file-document-multiple-outline</v-icon>
              <span class="text-h6">Recent Documents</span>
            </div>
            <v-btn variant="text" color="primary" @click="$router.push('/documents')">
              View All
              <v-icon right size="small">mdi-arrow-right</v-icon>
            </v-btn>
          </v-card-title>
          <v-divider></v-divider>
          
          <v-card-text v-if="loading" class="text-center py-12">
            <v-progress-circular indeterminate color="primary" size="64"></v-progress-circular>
            <p class="text-subtitle-1 mt-4">Loading documents...</p>
          </v-card-text>

          <v-card-text v-else-if="recentDocuments.length === 0" class="text-center py-12">
            <v-icon size="80" color="grey-lighten-2">mdi-file-document-outline</v-icon>
            <p class="text-h6 mt-4 text-grey">No documents yet</p>
            <p class="text-body-2 text-grey">Upload your first RFP document to get started</p>
            <v-btn color="primary" class="mt-4" @click="$router.push('/upload')">
              <v-icon left>mdi-plus</v-icon>
              Upload Document
            </v-btn>
          </v-card-text>

          <v-list v-else class="pa-0">
            <v-list-item
              v-for="(doc, index) in recentDocuments"
              :key="doc.id"
              :class="{ 'bg-grey-lighten-5': index % 2 === 0 }"
              @click="viewDocument(doc)"
              class="py-3"
            >
              <template v-slot:prepend>
                <v-avatar :color="getStatusColor(doc.status)" variant="tonal" size="48">
                  <v-icon>{{ getFileIcon(doc.file_name) }}</v-icon>
                </v-avatar>
              </template>

              <v-list-item-title class="text-subtitle-1 font-weight-medium mb-1">
                {{ doc.file_name }}
              </v-list-item-title>
              
              <v-list-item-subtitle class="d-flex align-center flex-wrap ga-2 mt-1">
                <v-chip size="x-small" :color="getStatusColor(doc.status)" variant="flat">
                  <v-icon v-if="doc.status === 'processing'" left size="12" class="mdi-spin">mdi-loading</v-icon>
                  <v-icon v-else-if="doc.status === 'completed'" left size="12">mdi-check</v-icon>
                  <v-icon v-else left size="12">mdi-clock</v-icon>
                  {{ doc.status }}
                </v-chip>
                <span class="text-caption">•</span>
                <span class="text-caption">{{ doc.records_processed || 0 }} records</span>
                <span class="text-caption">•</span>
                <span class="text-caption">{{ formatFileSize(doc.file_size) }}</span>
                <span class="text-caption">•</span>
                <span class="text-caption">{{ formatDate(doc.created_at) }}</span>
              </v-list-item-subtitle>

              <template v-slot:append>
                <v-btn icon variant="text" size="small" @click.stop="viewDocument(doc)">
                  <v-icon>mdi-chevron-right</v-icon>
                </v-btn>
              </template>
            </v-list-item>
          </v-list>
        </v-card>
      </v-col>

      <v-col cols="12" md="4">
        <v-card class="h-full">
          <v-card-title class="d-flex align-center">
            <v-icon left color="purple">mdi-chart-donut</v-icon>
            <span class="text-h6">Product Distribution</span>
          </v-card-title>
          <v-divider></v-divider>
          
          <v-card-text v-if="Object.keys(stats.productDistribution || {}).length > 0">
            <div
              v-for="(count, product) in stats.productDistribution"
              :key="product"
              class="mb-4"
            >
              <div class="d-flex justify-space-between align-center mb-2">
                <span class="text-subtitle-2 font-weight-medium">{{ product }}</span>
                <v-chip size="small" color="primary" variant="tonal">
                  {{ count }} 
                </v-chip>
              </div>
              <v-progress-linear
                :model-value="(count / stats.totalRecords) * 100"
                color="primary"
                height="10"
                rounded
                class="mb-1"
              ></v-progress-linear>
              <div class="text-caption text-grey text-right">
                {{ Math.round((count / stats.totalRecords) * 100) }}% of total
              </div>
            </div>
          </v-card-text>
          
          <v-card-text v-else class="text-center py-12">
            <v-icon size="64" color="grey-lighten-2">mdi-chart-bar-stacked</v-icon>
            <p class="text-subtitle-1 mt-4 text-grey">No data yet</p>
            <p class="text-caption text-grey">Product distribution will appear here</p>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Quick Actions -->
    <v-row>
      <v-col cols="12">
        <v-card>
          <v-card-title class="d-flex align-center">
            <v-icon left color="blue">mdi-lightning-bolt</v-icon>
            <span class="text-h6">Quick Actions</span>
          </v-card-title>
          <v-divider></v-divider>
          <v-card-text>
            <v-row>
              <v-col cols="12" sm="6" md="3">
                <v-card
                  hover
                  @click="$router.push('/upload')"
                  class="pa-4 text-center cursor-pointer"
                  color="blue-lighten-5"
                >
                  <v-avatar color="blue" size="56" class="mb-3">
                    <v-icon size="32" color="white">mdi-cloud-upload</v-icon>
                  </v-avatar>
                  <p class="text-subtitle-1 font-weight-bold mb-1">Upload Document</p>
                  <p class="text-caption text-grey">Add new RFP files</p>
                </v-card>
              </v-col>
              
              <v-col cols="12" sm="6" md="3">
                <v-card
                  hover
                  @click="$router.push('/search')"
                  class="pa-4 text-center cursor-pointer"
                  color="green-lighten-5"
                >
                  <v-avatar color="green" size="56" class="mb-3">
                    <v-icon size="32" color="white">mdi-robot</v-icon>
                  </v-avatar>
                  <p class="text-subtitle-1 font-weight-bold mb-1">Intelligent Q&A</p>
                  <p class="text-caption text-grey">Ask questions</p>
                </v-card>
              </v-col>
              
              <v-col cols="12" sm="6" md="3">
                <v-card
                  hover
                  @click="$router.push('/documents')"
                  class="pa-4 text-center cursor-pointer"
                  color="purple-lighten-5"
                >
                  <v-avatar color="purple" size="56" class="mb-3">
                    <v-icon size="32" color="white">mdi-file-document-multiple</v-icon>
                  </v-avatar>
                  <p class="text-subtitle-1 font-weight-bold mb-1">View Documents</p>
                  <p class="text-caption text-grey">Manage all files</p>
                </v-card>
              </v-col>
              
              <v-col cols="12" sm="6" md="3">
                <v-card
                  hover
                  @click="$router.push('/templates')"
                  class="pa-4 text-center cursor-pointer"
                  color="orange-lighten-5"
                >
                  <v-avatar color="orange" size="56" class="mb-3">
                    <v-icon size="32" color="white">mdi-table-cog</v-icon>
                  </v-avatar>
                  <p class="text-subtitle-1 font-weight-bold mb-1">Column Mapping</p>
                  <p class="text-caption text-grey">Manage templates</p>
                </v-card>
              </v-col>
            </v-row>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </div>
</template>

<script>
import axios from 'axios'
import { format } from 'date-fns'

export default {
  name: 'DashboardView',
  data() {
    return {
      loading: false,
      recentDocuments: [],
      refreshInterval: null
    }
  },
  computed: {
    stats() {
      return this.$store.state.stats
    }
  },
  mounted() {
    this.loadDashboardData()
    // Auto-refresh every 10 seconds
    this.refreshInterval = setInterval(this.loadDashboardData, 10000)
  },
  beforeUnmount() {
    if (this.refreshInterval) {
      clearInterval(this.refreshInterval)
    }
  },
  methods: {
    async loadDashboardData() {
      try {
        // Load stats
        await this.$store.dispatch('getStats')
        
        // Load recent documents
        this.loading = true
        const API_URL = process.env.VUE_APP_API_URL || 'http://localhost:5000/api'
        const response = await axios.get(`${API_URL}/documents`, {
          params: {
            page: 1,
            limit: 5
          }
        })
        this.recentDocuments = response.data.documents || []
      } catch (error) {
        console.error('Failed to load dashboard data:', error)
      } finally {
        this.loading = false
      }
    },
    
    getTotalProducts() {
      const products = this.stats.productDistribution || {}
      return Object.values(products).reduce((sum, count) => sum + count, 0)
    },
    
    viewDocument() {
      this.$router.push('/documents')
    },
    
    formatDate(dateString) {
      if (!dateString) return 'N/A'
      try {
        return format(new Date(dateString), 'MMM d, yyyy')
      } catch {
        return 'Recently'
      }
    },
    
    formatFileSize(bytes) {
      if (!bytes) return '0 B'
      const k = 1024
      const sizes = ['B', 'KB', 'MB', 'GB']
      const i = Math.floor(Math.log(bytes) / Math.log(k))
      return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
    },
    
    getStatusColor(status) {
      const colors = {
        'completed': 'success',
        'processing': 'info',
        'awaiting_mapping': 'warning',
        'failed': 'error'
      }
      return colors[status] || 'grey'
    },
    
    getFileIcon(filename) {
      if (!filename) return 'mdi-file'
      if (filename.endsWith('.xlsx') || filename.endsWith('.xls')) return 'mdi-file-excel'
      if (filename.endsWith('.pdf')) return 'mdi-file-pdf-box'
      if (filename.endsWith('.docx') || filename.endsWith('.doc')) return 'mdi-file-word'
      return 'mdi-file-document'
    }
  }
}
</script>

<style scoped>
.cursor-pointer {
  cursor: pointer;
}

.mdi-spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
</style>