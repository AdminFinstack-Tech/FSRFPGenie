<template>
  <div class="dashboard-professional">
    <!-- Page Header -->
    <div class="page-header">
      <h1 class="page-title">Dashboard</h1>
      <p class="page-description">Overview of your RFP documents and recent activity</p>
    </div>

    <!-- Stats Grid -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon-wrapper">
          <v-icon size="24" color="#14b8a6">mdi-file-document-multiple</v-icon>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ totalDocuments }}</div>
          <div class="stat-label">Total Documents</div>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon-wrapper">
          <v-icon size="24" color="#22c55e">mdi-check-circle</v-icon>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ completedDocuments }}</div>
          <div class="stat-label">Completed</div>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon-wrapper">
          <v-icon size="24" color="#f59e0b">mdi-clock-outline</v-icon>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ processingDocuments }}</div>
          <div class="stat-label">Processing</div>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon-wrapper">
          <v-icon size="24" color="#ef4444">mdi-alert-circle</v-icon>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ failedDocuments }}</div>
          <div class="stat-label">Failed</div>
        </div>
      </div>
    </div>

    <!-- Quick Actions -->
    <div class="quick-actions">
      <h2 class="section-title">Quick Actions</h2>
      <div class="actions-grid">
        <router-link to="/upload" class="action-card">
          <v-icon size="32" color="#14b8a6">mdi-cloud-upload</v-icon>
          <div class="action-title">Upload Document</div>
          <div class="action-description">Upload new RFP or documentation</div>
        </router-link>

        <router-link to="/search" class="action-card">
          <v-icon size="32" color="#14b8a6">mdi-magnify</v-icon>
          <div class="action-title">Search RFPs</div>
          <div class="action-description">Find requirements and responses</div>
        </router-link>

        <router-link to="/documents" class="action-card">
          <v-icon size="32" color="#14b8a6">mdi-file-document-multiple</v-icon>
          <div class="action-title">View Documents</div>
          <div class="action-description">Browse all uploaded documents</div>
        </router-link>

        <router-link to="/templates" class="action-card">
          <v-icon size="32" color="#14b8a6">mdi-text-box-multiple</v-icon>
          <div class="action-title">Templates</div>
          <div class="action-description">Manage RFP templates</div>
        </router-link>
      </div>
    </div>

    <!-- Recent Activity -->
    <div class="recent-activity">
      <h2 class="section-title">Recent Activity</h2>
      <div class="activity-card">
        <div v-if="loading" class="loading-state">
          <v-progress-circular indeterminate color="#14b8a6"></v-progress-circular>
          <p class="loading-text">Loading recent documents...</p>
        </div>

        <div v-else-if="recentDocuments.length === 0" class="empty-state">
          <v-icon size="48" color="#cbd5e1">mdi-file-document-outline</v-icon>
          <p class="empty-text">No documents yet</p>
          <p class="empty-subtext">Upload your first RFP to get started</p>
        </div>

        <div v-else class="activity-list">
          <div v-for="doc in recentDocuments" :key="doc.id" class="activity-item">
            <div class="activity-icon">
              <v-icon :color="getFileIconColor(doc.file_name)">
                {{ getFileIcon(doc.file_name) }}
              </v-icon>
            </div>
            <div class="activity-details">
              <div class="activity-name">{{ doc.file_name }}</div>
              <div class="activity-meta">
                <span class="activity-date">{{ formatDate(doc.created_at) }}</span>
                <span class="activity-separator">•</span>
                <span class="activity-size">{{ formatFileSize(doc.file_size) }}</span>
              </div>
            </div>
            <div class="activity-status">
              <span :class="['status-badge', `status-${doc.status}`]">
                {{ doc.status }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'DashboardProfessional',
  data() {
    return {
      loading: true,
      documents: [],
      recentDocuments: []
    }
  },
  computed: {
    totalDocuments() {
      return this.documents.length
    },
    completedDocuments() {
      return this.documents.filter(d => d.status === 'completed').length
    },
    processingDocuments() {
      return this.documents.filter(d => d.status === 'processing' || d.status === 'awaiting_mapping').length
    },
    failedDocuments() {
      return this.documents.filter(d => d.status === 'failed').length
    }
  },
  mounted() {
    this.loadDocuments()
  },
  methods: {
    async loadDocuments() {
      try {
        this.loading = true
        const API_URL = process.env.VUE_APP_API_URL || 'http://localhost:5000/api'
        const response = await axios.get(`${API_URL}/documents`)
        this.documents = response.data.documents || []
        this.recentDocuments = this.documents.slice(0, 5)
      } catch (error) {
        console.error('Error loading documents:', error)
      } finally {
        this.loading = false
      }
    },
    getFileIcon(filename) {
      const ext = filename.split('.').pop().toLowerCase()
      if (ext === 'xlsx' || ext === 'xls') return 'mdi-file-excel'
      if (ext === 'pdf') return 'mdi-file-pdf-box'
      if (ext === 'docx' || ext === 'doc') return 'mdi-file-word'
      return 'mdi-file-document'
    },
    getFileIconColor(filename) {
      const ext = filename.split('.').pop().toLowerCase()
      if (ext === 'xlsx' || ext === 'xls') return '#22c55e'
      if (ext === 'pdf') return '#ef4444'
      if (ext === 'docx' || ext === 'doc') return '#3b82f6'
      return '#64748b'
    },
    formatDate(dateStr) {
      if (!dateStr) return 'Unknown'
      const date = new Date(dateStr)
      return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
    },
    formatFileSize(bytes) {
      if (!bytes) return '0 KB'
      if (bytes < 1024) return bytes + ' B'
      if (bytes < 1048576) return (bytes / 1024).toFixed(1) + ' KB'
      return (bytes / 1048576).toFixed(1) + ' MB'
    }
  }
}
</script>

<style scoped>
/* === Color System === */
.dashboard-professional {
  --slate-50:  #f8fafc;
  --slate-100: #f1f5f9;
  --slate-200: #e2e8f0;
  --slate-300: #cbd5e1;
  --slate-400: #94a3b8;
  --slate-500: #64748b;
  --slate-600: #475569;
  --slate-700: #334155;
  --slate-800: #1e293b;
  --slate-900: #0f172a;
  --teal-500: #14b8a6;
  --teal-600: #0d9488;
}

.dashboard-professional {
  padding: 0;
}

/* === Page Header === */
.page-header {
  padding: 32px 0 24px 0;
  border-bottom: 1px solid var(--slate-200);
  margin-bottom: 32px;
}

.page-title {
  font-size: 24px;
  font-weight: 700;
  color: var(--slate-900);
  margin: 0 0 8px 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}

.page-description {
  font-size: 16px;
  color: var(--slate-600);
  margin: 0;
}

/* === Stats Grid === */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 16px;
  margin-bottom: 48px;
}

.stat-card {
  background-color: white;
  border: 1px solid var(--slate-200);
  border-radius: 8px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  transition: border-color 0.2s ease;
}

.stat-card:hover {
  border-color: var(--teal-500);
}

.stat-icon-wrapper {
  width: 48px;
  height: 48px;
  background-color: var(--slate-50);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.stat-content {
  flex: 1;
}

.stat-value {
  font-size: 30px;
  font-weight: 700;
  color: var(--slate-900);
  line-height: 1;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 14px;
  color: var(--slate-600);
  font-weight: 500;
}

/* === Sections === */
.section-title {
  font-size: 18px;
  font-weight: 600;
  color: var(--slate-900);
  margin: 0 0 16px 0;
}

/* === Quick Actions === */
.quick-actions {
  margin-bottom: 48px;
}

.actions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 16px;
}

.action-card {
  background-color: white;
  border: 1px solid var(--slate-200);
  border-radius: 8px;
  padding: 24px;
  text-decoration: none;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  transition: all 0.2s ease;
}

.action-card:hover {
  border-color: var(--teal-500);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.action-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--slate-900);
  margin: 12px 0 4px 0;
}

.action-description {
  font-size: 14px;
  color: var(--slate-600);
}

/* === Recent Activity === */
.activity-card {
  background-color: white;
  border: 1px solid var(--slate-200);
  border-radius: 8px;
  padding: 24px;
}

.loading-state,
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 48px 24px;
  text-align: center;
}

.loading-text,
.empty-text {
  font-size: 16px;
  color: var(--slate-700);
  margin: 16px 0 0 0;
}

.empty-subtext {
  font-size: 14px;
  color: var(--slate-500);
  margin: 4px 0 0 0;
}

.activity-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.activity-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  border-radius: 6px;
  transition: background-color 0.2s ease;
}

.activity-item:hover {
  background-color: var(--slate-50);
}

.activity-icon {
  width: 40px;
  height: 40px;
  background-color: var(--slate-50);
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.activity-details {
  flex: 1;
  min-width: 0;
}

.activity-name {
  font-size: 14px;
  font-weight: 500;
  color: var(--slate-900);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.activity-meta {
  font-size: 12px;
  color: var(--slate-500);
  margin-top: 2px;
}

.activity-separator {
  margin: 0 6px;
}

.activity-status {
  flex-shrink: 0;
}

.status-badge {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

.status-completed {
  background-color: #f0fdf4;
  color: #15803d;
  border: 1px solid #bbf7d0;
}

.status-processing,
.status-awaiting_mapping {
  background-color: #fffbeb;
  color: #92400e;
  border: 1px solid #fde68a;
}

.status-failed {
  background-color: #fef2f2;
  color: #991b1b;
  border: 1px solid #fecaca;
}

/* === Responsive === */
@media (max-width: 768px) {
  .stats-grid,
  .actions-grid {
    grid-template-columns: 1fr;
  }
}
</style>
