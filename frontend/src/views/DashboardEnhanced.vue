<template>
  <div class="enhanced-dashboard">
    <!-- Animated Gradient Header -->
    <div class="dashboard-header">
      <div class="header-bg-animated"></div>
      <div class="header-content">
        <div class="welcome-section">
          <h1 class="display-1">{{ getGreeting() }} 👋</h1>
          <p class="text-h6 mt-2 header-subtitle">{{ welcomeMessage }}</p>
        </div>
        
        <!-- System Health Indicators -->
        <div class="system-health">
          <v-chip class="health-chip" :color="systemHealth.azure ? 'success' : 'error'" variant="flat">
            <v-icon left size="small">{{ systemHealth.azure ? 'mdi-check-circle' : 'mdi-alert-circle' }}</v-icon>
            AI {{ systemHealth.azure ? 'Online' : 'Offline' }}
          </v-chip>
          <v-chip class="health-chip" :color="systemHealth.database ? 'success' : 'error'" variant="flat">
            <v-icon left size="small">{{ systemHealth.database ? 'mdi-database-check' : 'mdi-database-alert' }}</v-icon>
            DB {{ systemHealth.database ? 'Connected' : 'Disconnected' }}
          </v-chip>
          <v-chip class="health-chip" color="info" variant="flat">
            <v-icon left size="small">mdi-clock-outline</v-icon>
            {{ currentTime }}
          </v-chip>
        </div>
      </div>
    </div>

    <!-- Quick Search Bar -->
    <v-card class="quick-search-card mb-6" elevation="4">
      <v-card-text class="pa-4">
        <div class="d-flex align-center ga-3">
          <v-icon size="32" color="primary">mdi-magnify</v-icon>
          <v-text-field
            v-model="quickSearch"
            placeholder="Quick search across all documents..."
            variant="solo-filled"
            density="comfortable"
            hide-details
            @keyup.enter="performQuickSearch"
            class="flex-grow-1"
          >
            <template v-slot:append-inner>
              <v-btn icon size="small" variant="text" @click="startVoiceSearch">
                <v-icon>mdi-microphone</v-icon>
              </v-btn>
            </template>
          </v-text-field>
          <v-btn color="primary" size="large" @click="performQuickSearch">
            Search
          </v-btn>
        </div>
      </v-card-text>
    </v-card>

    <!-- Animated Statistics Cards -->
    <v-row class="mb-6">
      <v-col cols="12" sm="6" md="3" v-for="(stat, index) in enhancedStats" :key="index">
        <v-card 
          class="stat-card" 
          :class="`stat-card-${index}`"
          hover
          @click="navigateTo(stat.route)"
        >
          <div class="stat-card-glow" :style="{ background: stat.gradient }"></div>
          <v-card-text class="pa-6">
            <div class="d-flex justify-space-between align-center mb-4">
              <v-avatar :color="stat.color" size="64" class="stat-avatar">
                <v-icon size="32" color="white">{{ stat.icon }}</v-icon>
              </v-avatar>
              <v-chip :color="stat.trendColor" variant="flat" size="small">
                <v-icon left size="small">{{ stat.trendIcon }}</v-icon>
                {{ stat.trend }}
              </v-chip>
            </div>
            
            <div class="stat-value-container">
              <span class="stat-value" :data-target="stat.value">{{ animatedValues[index] || 0 }}</span>
              <span class="stat-sparkline">{{ stat.sparkline }}</span>
            </div>
            
            <p class="stat-label mt-2">{{ stat.label }}</p>
            <p class="stat-sublabel text-caption text-grey">{{ stat.sublabel }}</p>
            
            <!-- Mini Progress Bar -->
            <v-progress-linear
              v-if="stat.progress"
              :model-value="stat.progress"
              :color="stat.color"
              height="4"
              rounded
              class="mt-3"
            ></v-progress-linear>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Charts and Activity Row -->
    <v-row class="mb-6">
      <!-- Upload Trends Chart -->
      <v-col cols="12" md="8">
        <v-card class="chart-card" elevation="3">
          <v-card-title class="d-flex justify-space-between align-center">
            <div class="d-flex align-center">
              <v-icon left color="primary">mdi-chart-line</v-icon>
              <span class="text-h6">Upload Activity</span>
            </div>
            <v-btn-toggle v-model="chartPeriod" mandatory density="compact" variant="outlined">
              <v-btn value="week" size="small">Week</v-btn>
              <v-btn value="month" size="small">Month</v-btn>
              <v-btn value="year" size="small">Year</v-btn>
            </v-btn-toggle>
          </v-card-title>
          <v-divider></v-divider>
          <v-card-text>
            <LineChart v-if="chartData.labels.length > 0" :data="chartData" :options="chartOptions" />
            <div v-else class="text-center py-12">
              <v-icon size="80" color="grey-lighten-2">mdi-chart-line-variant</v-icon>
              <p class="text-h6 mt-4 text-grey">No data yet</p>
              <p class="text-caption text-grey">Upload trends will appear here</p>
            </div>
          </v-card-text>
        </v-card>
      </v-col>

      <!-- Activity Feed -->
      <v-col cols="12" md="4">
        <v-card class="activity-feed-card" elevation="3">
          <v-card-title class="d-flex justify-space-between align-center">
            <div class="d-flex align-center">
              <v-icon left color="success">mdi-timeline</v-icon>
              <span class="text-h6">Live Activity</span>
            </div>
            <v-chip color="success" variant="flat" size="x-small">
              <span class="pulse-dot"></span>
              Live
            </v-chip>
          </v-card-title>
          <v-divider></v-divider>
          
          <v-card-text class="pa-0 activity-feed-container">
            <v-list class="pa-0">
              <v-list-item
                v-for="(activity, index) in recentActivities"
                :key="index"
                class="activity-item"
              >
                <template v-slot:prepend>
                  <v-avatar :color="activity.color" size="40" variant="tonal">
                    <v-icon size="20">{{ activity.icon }}</v-icon>
                  </v-avatar>
                </template>

                <v-list-item-title class="text-subtitle-2">
                  {{ activity.title }}
                </v-list-item-title>
                <v-list-item-subtitle class="text-caption">
                  {{ activity.time }}
                </v-list-item-subtitle>
              </v-list-item>
            </v-list>

            <div v-if="recentActivities.length === 0" class="text-center py-8">
              <v-icon size="48" color="grey-lighten-2">mdi-timeline-clock</v-icon>
              <p class="text-caption text-grey mt-2">No recent activity</p>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Product Distribution and Recent Documents -->
    <v-row class="mb-6">
      <!-- Product Distribution with Donut Chart -->
      <v-col cols="12" md="4">
        <v-card class="chart-card" elevation="3">
          <v-card-title class="d-flex align-center">
            <v-icon left color="purple">mdi-chart-donut</v-icon>
            <span class="text-h6">Product Distribution</span>
          </v-card-title>
          <v-divider></v-divider>
          
          <v-card-text>
            <Doughnut v-if="hasProducts" :data="donutChartData" :options="donutChartOptions" />
            
            <div v-if="hasProducts" class="mt-4">
              <div
                v-for="(count, product) in stats.productDistribution"
                :key="product"
                class="product-item mb-3"
              >
                <div class="d-flex justify-space-between align-center mb-1">
                  <div class="d-flex align-center">
                    <div class="product-color" :style="{ background: donutColors[Object.keys(stats.productDistribution).indexOf(product) % donutColors.length] }"></div>
                    <span class="text-subtitle-2">{{ product }}</span>
                  </div>
                  <v-chip size="x-small" :color="donutColors[Object.keys(stats.productDistribution).indexOf(product) % donutColors.length]" variant="flat">
                    {{ count }}
                  </v-chip>
                </div>
                <v-progress-linear
                  :model-value="(count / stats.totalRecords) * 100"
                  :color="donutColors[Object.keys(stats.productDistribution).indexOf(product) % donutColors.length]"
                  height="6"
                  rounded
                ></v-progress-linear>
              </div>
            </div>

            <div v-else class="text-center py-8">
              <v-icon size="64" color="grey-lighten-2">mdi-chart-donut</v-icon>
              <p class="text-subtitle-2 mt-3 text-grey">No products yet</p>
              <p class="text-caption text-grey">Distribution will appear here</p>
            </div>
          </v-card-text>
        </v-card>
      </v-col>

      <!-- Recent Documents -->
      <v-col cols="12" md="8">
        <v-card class="documents-card" elevation="3">
          <v-card-title class="d-flex justify-space-between align-center">
            <div class="d-flex align-center">
              <v-icon left color="primary">mdi-file-document-multiple</v-icon>
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
              <v-icon left>mdi-cloud-upload</v-icon>
              Upload Document
            </v-btn>
          </v-card-text>

          <v-list v-else class="pa-0">
            <v-list-item
              v-for="doc in recentDocuments"
              :key="doc.id"
              class="document-item"
              @click="viewDocument"
            >
              <template v-slot:prepend>
                <v-avatar :color="getStatusColor(doc.status)" variant="tonal" size="48">
                  <v-icon>{{ getFileIcon(doc.file_name) }}</v-icon>
                </v-avatar>
              </template>

              <v-list-item-title class="text-subtitle-1 font-weight-medium">
                {{ doc.file_name }}
              </v-list-item-title>
              
              <v-list-item-subtitle class="d-flex align-center flex-wrap ga-2 mt-1">
                <v-chip size="x-small" :color="getStatusColor(doc.status)" variant="flat">
                  <v-icon v-if="doc.status === 'processing'" left size="12" class="spinning-icon">mdi-loading</v-icon>
                  <v-icon v-else-if="doc.status === 'completed'" left size="12">mdi-check</v-icon>
                  <v-icon v-else left size="12">mdi-clock</v-icon>
                  {{ doc.status }}
                </v-chip>
                <span class="text-caption">•</span>
                <span class="text-caption">{{ doc.records_processed || 0 }} records</span>
                <span class="text-caption">•</span>
                <span class="text-caption">{{ formatDate(doc.created_at) }}</span>
              </v-list-item-subtitle>

              <template v-slot:append>
                <v-btn icon variant="text" size="small">
                  <v-icon>mdi-chevron-right</v-icon>
                </v-btn>
              </template>
            </v-list-item>
          </v-list>
        </v-card>
      </v-col>
    </v-row>

    <!-- Quick Actions with Animations -->
    <v-card class="quick-actions-card mb-6" elevation="3">
      <v-card-title class="d-flex align-center">
        <v-icon left color="blue">mdi-lightning-bolt</v-icon>
        <span class="text-h6">Quick Actions</span>
      </v-card-title>
      <v-divider></v-divider>
      <v-card-text>
        <v-row>
          <v-col cols="12" sm="6" md="3" v-for="(action, index) in quickActions" :key="index">
            <v-card
              hover
              @click="navigateTo(action.route)"
              class="action-card"
              :class="`action-card-${index}`"
            >
              <div class="action-glow" :style="{ background: action.gradient }"></div>
              <v-card-text class="pa-4 text-center">
                <v-avatar :color="action.color" size="64" class="action-avatar mb-3">
                  <v-icon size="32" color="white">{{ action.icon }}</v-icon>
                </v-avatar>
                <p class="text-subtitle-1 font-weight-bold mb-1">{{ action.title }}</p>
                <p class="text-caption text-grey">{{ action.description }}</p>
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>
      </v-card-text>
    </v-card>
  </div>
</template>

<script>
import axios from 'axios'
import { format } from 'date-fns'
import { Line as LineChart, Doughnut } from 'vue-chartjs'
import { Chart as ChartJS, Title, Tooltip, Legend, LineElement, PointElement, CategoryScale, LinearScale, ArcElement } from 'chart.js'

ChartJS.register(Title, Tooltip, Legend, LineElement, PointElement, CategoryScale, LinearScale, ArcElement)

export default {
  name: 'EnhancedDashboard',
  components: {
    LineChart,
    Doughnut
  },
  data() {
    return {
      loading: false,
      recentDocuments: [],
      refreshInterval: null,
      currentTime: '',
      quickSearch: '',
      chartPeriod: 'week',
      animatedValues: [],
      systemHealth: {
        azure: true,
        database: true
      },
      donutColors: ['#667eea', '#764ba2', '#f093fb', '#4facfe', '#00f2fe', '#43e97b', '#fa709a', '#fee140'],
      recentActivities: [],
      quickActions: [
        {
          title: 'Upload Document',
          description: 'Add new RFP files',
          icon: 'mdi-cloud-upload',
          color: 'blue',
          route: '/upload',
          gradient: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
        },
        {
          title: 'Intelligent Q&A',
          description: 'Ask AI questions',
          icon: 'mdi-robot-excited',
          color: 'green',
          route: '/search',
          gradient: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)'
        },
        {
          title: 'View Documents',
          description: 'Manage all files',
          icon: 'mdi-file-document-multiple',
          color: 'purple',
          route: '/documents',
          gradient: 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)'
        },
        {
          title: 'Column Mapping',
          description: 'Configure templates',
          icon: 'mdi-table-cog',
          color: 'orange',
          route: '/column-mapping',
          gradient: 'linear-gradient(135deg, #a8edea 0%, #fed6e3 100%)'
        }
      ]
    }
  },
  computed: {
    stats() {
      return this.$store.state.stats
    },
    enhancedStats() {
      return [
        {
          label: 'Total Documents',
          sublabel: 'Across all RFPs',
          value: this.stats.totalDocuments || 0,
          icon: 'mdi-file-document-multiple',
          color: 'blue',
          trend: '+12%',
          trendColor: 'success',
          trendIcon: 'mdi-trending-up',
          sparkline: '▁▃▅▆▇',
          progress: 75,
          route: '/documents',
          gradient: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
        },
        {
          label: 'Total Records',
          sublabel: 'Indexed requirements',
          value: this.stats.totalRecords || 0,
          icon: 'mdi-database',
          color: 'green',
          trend: '+8%',
          trendColor: 'success',
          trendIcon: 'mdi-trending-up',
          sparkline: '▃▅▆▇▉',
          progress: 82,
          route: '/search',
          gradient: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)'
        },
        {
          label: 'Product Items',
          sublabel: `${Object.keys(this.stats.productDistribution || {}).length} categories`,
          value: this.getTotalProducts(),
          icon: 'mdi-package-variant',
          color: 'purple',
          trend: '+5%',
          trendColor: 'success',
          trendIcon: 'mdi-trending-up',
          sparkline: '▂▄▆▇▅',
          progress: 68,
          route: '/search',
          gradient: 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)'
        },
        {
          label: 'Searches Today',
          sublabel: 'AI-powered queries',
          value: this.stats.totalSearches || 0,
          icon: 'mdi-magnify',
          color: 'orange',
          trend: '+15%',
          trendColor: 'success',
          trendIcon: 'mdi-trending-up',
          sparkline: '▁▂▄▆▇',
          progress: 90,
          route: '/search',
          gradient: 'linear-gradient(135deg, #a8edea 0%, #fed6e3 100%)'
        }
      ]
    },
    hasProducts() {
      return Object.keys(this.stats.productDistribution || {}).length > 0
    },
    chartData() {
      // Generate sample data for the chart
      const labels = this.getChartLabels()
      return {
        labels,
        datasets: [
          {
            label: 'Uploads',
            data: this.generateChartData(labels.length),
            borderColor: '#667eea',
            backgroundColor: 'rgba(102, 126, 234, 0.1)',
            tension: 0.4,
            fill: true
          }
        ]
      }
    },
    chartOptions() {
      return {
        responsive: true,
        maintainAspectRatio: true,
        aspectRatio: 2.5,
        plugins: {
          legend: {
            display: false
          },
          tooltip: {
            backgroundColor: 'rgba(0, 0, 0, 0.8)',
            padding: 12,
            titleColor: '#fff',
            bodyColor: '#fff',
            borderColor: '#667eea',
            borderWidth: 1
          }
        },
        scales: {
          y: {
            beginAtZero: true,
            grid: {
              color: 'rgba(0, 0, 0, 0.05)'
            }
          },
          x: {
            grid: {
              display: false
            }
          }
        }
      }
    },
    donutChartData() {
      const products = this.stats.productDistribution || {}
      return {
        labels: Object.keys(products),
        datasets: [
          {
            data: Object.values(products),
            backgroundColor: this.donutColors,
            borderWidth: 0,
            hoverOffset: 10
          }
        ]
      }
    },
    donutChartOptions() {
      return {
        responsive: true,
        maintainAspectRatio: true,
        aspectRatio: 1.5,
        plugins: {
          legend: {
            display: false
          },
          tooltip: {
            backgroundColor: 'rgba(0, 0, 0, 0.8)',
            padding: 12
          }
        },
        cutout: '65%'
      }
    },
    welcomeMessage() {
      const hour = new Date().getHours()
      if (hour < 12) return 'Ready to tackle some RFPs this morning?'
      if (hour < 17) return 'Let\'s power through those requirements!'
      return 'Wrapping up the day? Great work so far!'
    }
  },
  mounted() {
    this.loadDashboardData()
    this.updateTime()
    this.animateStatValues()
    this.checkSystemHealth()
    this.loadRecentActivity()
    
    // Auto-refresh every 10 seconds
    this.refreshInterval = setInterval(() => {
      this.loadDashboardData()
      this.updateTime()
      this.loadRecentActivity()
    }, 10000)
  },
  beforeUnmount() {
    if (this.refreshInterval) {
      clearInterval(this.refreshInterval)
    }
  },
  methods: {
    getGreeting() {
      const hour = new Date().getHours()
      if (hour < 12) return 'Good Morning'
      if (hour < 17) return 'Good Afternoon'
      return 'Good Evening'
    },
    
    updateTime() {
      this.currentTime = format(new Date(), 'HH:mm:ss')
    },
    
    async loadDashboardData() {
      try {
        await this.$store.dispatch('getStats')
        
        this.loading = true
        const API_URL = process.env.VUE_APP_API_URL || 'http://localhost:5001/api'
        const response = await axios.get(`${API_URL}/documents`, {
          params: { page: 1, limit: 5 }
        })
        this.recentDocuments = response.data.documents || []
      } catch (error) {
        console.error('Failed to load dashboard data:', error)
        this.systemHealth.database = false
      } finally {
        this.loading = false
      }
    },
    
    animateStatValues() {
      this.enhancedStats.forEach((stat, index) => {
        this.animateValue(index, 0, stat.value, 1000)
      })
    },
    
    animateValue(index, start, end, duration) {
      const range = end - start
      const increment = range / (duration / 16)
      let current = start
      
      const timer = setInterval(() => {
        current += increment
        if ((increment > 0 && current >= end) || (increment < 0 && current <= end)) {
          current = end
          clearInterval(timer)
        }
        // Vue 3: Direct assignment is reactive, no need for this.$set
        this.animatedValues[index] = Math.floor(current)
      }, 16)
    },
    
    async checkSystemHealth() {
      try {
        const API_URL = process.env.VUE_APP_API_URL || 'http://localhost:5001/api'
        await axios.get(`${API_URL}/health`)
        this.systemHealth.azure = true
        this.systemHealth.database = true
      } catch (error) {
        this.systemHealth.azure = false
      }
    },
    
    loadRecentActivity() {
      // Simulate recent activities
      this.recentActivities = [
        {
          title: 'Document uploaded',
          time: '2 minutes ago',
          icon: 'mdi-file-upload',
          color: 'blue'
        },
        {
          title: 'Processing completed',
          time: '5 minutes ago',
          icon: 'mdi-check-circle',
          color: 'success'
        },
        {
          title: 'AI search performed',
          time: '12 minutes ago',
          icon: 'mdi-robot',
          color: 'purple'
        },
        {
          title: 'Document indexed',
          time: '25 minutes ago',
          icon: 'mdi-database',
          color: 'green'
        }
      ]
    },
    
    getTotalProducts() {
      const products = this.stats.productDistribution || {}
      return Object.values(products).reduce((sum, count) => sum + count, 0)
    },
    
    getChartLabels() {
      if (this.chartPeriod === 'week') {
        return ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
      } else if (this.chartPeriod === 'month') {
        return ['Week 1', 'Week 2', 'Week 3', 'Week 4']
      } else {
        return ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
      }
    },
    
    generateChartData(length) {
      return Array.from({ length }, () => Math.floor(Math.random() * 20) + 5)
    },
    
    navigateTo(route) {
      if (route) {
        this.$router.push(route)
      }
    },
    
    viewDocument() {
      this.$router.push('/documents')
    },
    
    performQuickSearch() {
      if (this.quickSearch.trim()) {
        this.$router.push({ path: '/search', query: { q: this.quickSearch } })
      }
    },
    
    startVoiceSearch() {
      // Voice search implementation
      this.$toast.info('Voice search feature coming soon!')
    },
    
    formatDate(dateString) {
      if (!dateString) return 'Recently'
      try {
        return format(new Date(dateString), 'MMM d, HH:mm')
      } catch {
        return 'Recently'
      }
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
.enhanced-dashboard {
  padding: 24px;
  background: linear-gradient(to bottom, #f8f9fa 0%, #ffffff 100%);
  min-height: 100vh;
}

/* Animated Header */
.dashboard-header {
  position: relative;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
  border-radius: 24px;
  padding: 48px 32px;
  margin-bottom: 32px;
  overflow: hidden;
  box-shadow: 0 20px 60px rgba(102, 126, 234, 0.3);
}

.header-bg-animated {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(45deg, transparent 30%, rgba(255, 255, 255, 0.1) 50%, transparent 70%);
  background-size: 200% 200%;
  animation: shimmer 3s ease-in-out infinite;
}

@keyframes shimmer {
  0%, 100% { background-position: 0% 0%; }
  50% { background-position: 100% 100%; }
}

.header-content {
  position: relative;
  z-index: 1;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 24px;
}

.welcome-section h1 {
  color: white;
  font-weight: 700;
  text-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

.header-subtitle {
  color: rgba(255, 255, 255, 0.95);
  font-weight: 400;
}

.system-health {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.health-chip {
  backdrop-filter: blur(10px);
  background: rgba(255, 255, 255, 0.2) !important;
  color: white !important;
}

/* Quick Search */
.quick-search-card {
  background: white;
  border-radius: 16px;
}

/* Animated Stat Cards */
.stat-card {
  position: relative;
  border-radius: 16px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.3s ease;
  animation: slideInUp 0.5s ease;
}

.stat-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
}

.stat-card-0 { animation-delay: 0s; }
.stat-card-1 { animation-delay: 0.1s; }
.stat-card-2 { animation-delay: 0.2s; }
.stat-card-3 { animation-delay: 0.3s; }

@keyframes slideInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.stat-card-glow {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.stat-card:hover .stat-card-glow {
  opacity: 1;
}

.stat-avatar {
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
}

.stat-value-container {
  display: flex;
  align-items: baseline;
  gap: 8px;
}

.stat-value {
  font-size: 2.5rem;
  font-weight: 700;
  color: #2c3e50;
  line-height: 1;
}

.stat-sparkline {
  font-size: 1.2rem;
  color: #4caf50;
  opacity: 0.7;
}

.stat-label {
  font-size: 0.95rem;
  font-weight: 600;
  color: #5a6c7d;
  margin: 0;
}

.stat-sublabel {
  font-size: 0.75rem;
  color: #9e9e9e;
}

/* Charts */
.chart-card {
  border-radius: 16px;
  animation: fadeIn 0.6s ease;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

/* Activity Feed */
.activity-feed-card {
  border-radius: 16px;
  max-height: 450px;
}

.activity-feed-container {
  max-height: 360px;
  overflow-y: auto;
}

.activity-item {
  transition: background 0.2s ease;
}

.activity-item:hover {
  background: rgba(102, 126, 234, 0.05);
}

.pulse-dot {
  display: inline-block;
  width: 8px;
  height: 8px;
  background: currentColor;
  border-radius: 50%;
  margin-right: 6px;
  animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
    transform: scale(1);
  }
  50% {
    opacity: 0.5;
    transform: scale(0.8);
  }
}

/* Product Distribution */
.product-item {
  transition: all 0.2s ease;
}

.product-color {
  width: 16px;
  height: 16px;
  border-radius: 4px;
  margin-right: 8px;
}

/* Documents */
.documents-card {
  border-radius: 16px;
}

.document-item {
  transition: all 0.2s ease;
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
}

.document-item:hover {
  background: rgba(102, 126, 234, 0.05);
}

.spinning-icon {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* Quick Actions */
.quick-actions-card {
  border-radius: 16px;
}

.action-card {
  position: relative;
  border-radius: 16px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.3s ease;
  animation: zoomIn 0.5s ease;
}

.action-card:hover {
  transform: scale(1.05);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
}

.action-card-0 { animation-delay: 0s; }
.action-card-1 { animation-delay: 0.1s; }
.action-card-2 { animation-delay: 0.2s; }
.action-card-3 { animation-delay: 0.3s; }

@keyframes zoomIn {
  from {
    opacity: 0;
    transform: scale(0.9);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

.action-glow {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.action-card:hover .action-glow {
  opacity: 1;
}

.action-avatar {
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2);
  transition: transform 0.3s ease;
}

.action-card:hover .action-avatar {
  transform: scale(1.1) rotate(5deg);
}

/* Responsive */
@media (max-width: 960px) {
  .enhanced-dashboard {
    padding: 16px;
  }
  
  .dashboard-header {
    padding: 32px 24px;
  }
  
  .welcome-section h1 {
    font-size: 2rem;
  }
}
</style>
