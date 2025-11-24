<template>
  <div class="documents-container-premium">
    <!-- Premium Page Header with Stats -->
    <div class="premium-header">
      <div class="header-content">
        <div class="title-section">
          <div class="icon-badge">
            <v-icon size="32" color="white">mdi-file-cabinet</v-icon>
          </div>
          <div>
            <h1 class="page-title">Document Library</h1>
            <p class="page-subtitle">Manage and track your uploaded documents</p>
          </div>
        </div>
        
        <v-btn
          class="upload-btn-premium"
          size="large"
          elevation="0"
          @click="$router.push('/upload')"
        >
          <v-icon left>mdi-cloud-upload</v-icon>
          Upload Document
        </v-btn>
      </div>

      <!-- Stats Cards -->
      <div class="stats-grid">
        <div class="stat-card-premium emerald">
          <div class="stat-icon">
            <v-icon size="28" color="white">mdi-check-circle</v-icon>
          </div>
          <div class="stat-details">
            <div class="stat-value">{{ completedCount }}</div>
            <div class="stat-label">Completed</div>
          </div>
        </div>

        <div class="stat-card-premium gold">
          <div class="stat-icon">
            <v-icon size="28" color="white">mdi-clock-outline</v-icon>
          </div>
          <div class="stat-details">
            <div class="stat-value">{{ processingCount }}</div>
            <div class="stat-label">Processing</div>
          </div>
        </div>

        <div class="stat-card-premium navy">
          <div class="stat-icon">
            <v-icon size="28" color="white">mdi-alert-circle</v-icon>
          </div>
          <div class="stat-details">
            <div class="stat-value">{{ failedCount }}</div>
            <div class="stat-label">Failed</div>
          </div>
        </div>

        <div class="stat-card-premium slate">
          <div class="stat-icon">
            <v-icon size="28" color="white">mdi-file-multiple</v-icon>
          </div>
          <div class="stat-details">
            <div class="stat-value">{{ documents.length }}</div>
            <div class="stat-label">Total Documents</div>
          </div>
        </div>
      </div>
    </div>

    <!-- Filters and Search -->
    <div class="filters-section">
      <v-text-field
        v-model="search"
        placeholder="Search documents..."
        prepend-inner-icon="mdi-magnify"
        variant="outlined"
        density="comfortable"
        hide-details
        class="search-field-premium"
      ></v-text-field>

      <v-select
        v-model="filterStatus"
        :items="statusFilters"
        placeholder="Filter by status"
        variant="outlined"
        density="comfortable"
        hide-details
        class="filter-select-premium"
      >
        <template v-slot:prepend-inner>
          <v-icon>mdi-filter-variant</v-icon>
        </template>
      </v-select>

      <v-select
        v-model="filterType"
        :items="typeFilters"
        placeholder="Filter by type"
        variant="outlined"
        density="comfortable"
        hide-details
        class="filter-select-premium"
      >
        <template v-slot:prepend-inner>
          <v-icon>mdi-file-document</v-icon>
        </template>
      </v-select>
    </div>

    <!-- Documents Grid/List View -->
    <div class="view-toggle">
      <v-btn-toggle v-model="viewMode" mandatory color="primary" class="toggle-premium">
        <v-btn value="grid" icon size="small">
          <v-icon>mdi-view-grid</v-icon>
        </v-btn>
        <v-btn value="list" icon size="small">
          <v-icon>mdi-view-list</v-icon>
        </v-btn>
      </v-btn-toggle>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="loading-container">
      <v-progress-circular indeterminate color="primary" size="64"></v-progress-circular>
      <p class="loading-text">Loading documents...</p>
    </div>

    <!-- Empty State -->
    <div v-else-if="filteredDocuments.length === 0" class="empty-state-premium">
      <div class="empty-icon">
        <v-icon size="80" color="#94A3B8">mdi-folder-open-outline</v-icon>
      </div>
      <h3 class="empty-title">No Documents Found</h3>
      <p class="empty-subtitle">Upload your first document to get started</p>
      <v-btn
        class="upload-btn-premium"
        size="large"
        elevation="2"
        @click="$router.push('/upload')"
      >
        <v-icon left>mdi-cloud-upload</v-icon>
        Upload Document
      </v-btn>
    </div>

    <!-- Grid View -->
    <div v-else-if="viewMode === 'grid'" class="documents-grid">
      <div
        v-for="doc in filteredDocuments"
        :key="doc._id"
        class="document-card-premium"
        @click="viewDocument(doc)"
      >
        <div class="card-header">
          <div class="file-icon-wrapper" :class="getFileTypeClass(doc.file_name)">
            <v-icon size="32" color="white">{{ getFileIcon(doc.file_name) }}</v-icon>
          </div>
          <v-menu offset-y>
            <template v-slot:activator="{ props }">
              <v-btn
                icon
                size="small"
                v-bind="props"
                class="menu-btn"
                @click.stop
              >
                <v-icon>mdi-dots-vertical</v-icon>
              </v-btn>
            </template>
            <v-list density="compact" class="menu-list-premium">
              <v-list-item @click.stop="viewDocument(doc)">
                <template v-slot:prepend>
                  <v-icon size="small">mdi-eye</v-icon>
                </template>
                <v-list-item-title>View Details</v-list-item-title>
              </v-list-item>
              
              <v-list-item 
                v-if="doc.status === 'awaiting_mapping'"
                @click.stop="$router.push(`/mapping/${doc.id}`)"
              >
                <template v-slot:prepend>
                  <v-icon size="small">mdi-table-edit</v-icon>
                </template>
                <v-list-item-title>Map Columns</v-list-item-title>
              </v-list-item>
              
              <v-list-item 
                v-if="doc.status === 'completed'"
                @click.stop="viewRecords(doc)"
              >
                <template v-slot:prepend>
                  <v-icon size="small">mdi-database</v-icon>
                </template>
                <v-list-item-title>View Records</v-list-item-title>
              </v-list-item>
              
              <v-divider></v-divider>
              
              <v-list-item @click.stop="deleteDocument(doc)" class="delete-item">
                <template v-slot:prepend>
                  <v-icon size="small" color="error">mdi-delete</v-icon>
                </template>
                <v-list-item-title class="text-error">Delete</v-list-item-title>
              </v-list-item>
            </v-list>
          </v-menu>
        </div>

        <div class="card-body">
          <h3 class="doc-title">{{ doc.file_name }}</h3>
          
          <div class="doc-metadata">
            <div class="metadata-item">
              <v-icon size="14" class="metadata-icon">mdi-file</v-icon>
              <span>{{ doc.document_type }}</span>
            </div>
            <div class="metadata-item">
              <v-icon size="14" class="metadata-icon">mdi-database</v-icon>
              <span>{{ doc.records_processed || 0 }} records</span>
            </div>
          </div>

          <div class="doc-info">
            <div v-if="doc.metadata?.bank_name" class="info-chip">
              <v-icon size="12" class="mr-1">mdi-bank</v-icon>
              {{ doc.metadata.bank_name }}
            </div>
            <div v-if="doc.metadata?.product" class="info-chip">
              <v-icon size="12" class="mr-1">mdi-package-variant</v-icon>
              {{ doc.metadata.product }}
            </div>
          </div>

          <div class="doc-footer">
            <div class="status-badge" :class="getStatusClass(doc.status)">
              <div class="status-dot"></div>
              <span>{{ doc.status }}</span>
            </div>
            <span class="doc-date">{{ formatDate(doc.created_at) }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- List View -->
    <div v-else class="documents-list">
      <div class="list-header">
        <div class="list-header-cell" style="flex: 2">Document</div>
        <div class="list-header-cell" style="flex: 1">Type</div>
        <div class="list-header-cell" style="flex: 1">Status</div>
        <div class="list-header-cell" style="flex: 1">Records</div>
        <div class="list-header-cell" style="flex: 1">Date</div>
        <div class="list-header-cell" style="width: 80px">Actions</div>
      </div>

      <div
        v-for="doc in filteredDocuments"
        :key="doc._id"
        class="list-row-premium"
        @click="viewDocument(doc)"
      >
        <div class="list-cell" style="flex: 2">
          <div class="file-info">
            <div class="file-icon-small" :class="getFileTypeClass(doc.file_name)">
              <v-icon size="20" color="white">{{ getFileIcon(doc.file_name) }}</v-icon>
            </div>
            <div class="file-details">
              <div class="file-name">{{ doc.file_name }}</div>
              <div class="file-size">{{ formatFileSize(doc.file_size) }}</div>
            </div>
          </div>
        </div>
        
        <div class="list-cell" style="flex: 1">
          <div class="type-badge">{{ doc.document_type }}</div>
        </div>
        
        <div class="list-cell" style="flex: 1">
          <div class="status-badge" :class="getStatusClass(doc.status)">
            <div class="status-dot"></div>
            <span>{{ doc.status }}</span>
          </div>
        </div>
        
        <div class="list-cell" style="flex: 1">
          <span class="records-count">{{ doc.records_processed || 0 }} / {{ doc.total_records || '-' }}</span>
        </div>
        
        <div class="list-cell" style="flex: 1">
          <span class="date-text">{{ formatDate(doc.created_at) }}</span>
        </div>
        
        <div class="list-cell" style="width: 80px">
          <v-menu offset-y>
            <template v-slot:activator="{ props }">
              <v-btn
                icon
                size="small"
                v-bind="props"
                class="menu-btn"
                @click.stop
              >
                <v-icon>mdi-dots-vertical</v-icon>
              </v-btn>
            </template>
            <v-list density="compact" class="menu-list-premium">
              <v-list-item @click.stop="viewDocument(doc)">
                <template v-slot:prepend>
                  <v-icon size="small">mdi-eye</v-icon>
                </template>
                <v-list-item-title>View Details</v-list-item-title>
              </v-list-item>
              
              <v-list-item 
                v-if="doc.status === 'awaiting_mapping'"
                @click.stop="$router.push(`/mapping/${doc.id}`)"
              >
                <template v-slot:prepend>
                  <v-icon size="small">mdi-table-edit</v-icon>
                </template>
                <v-list-item-title>Map Columns</v-list-item-title>
              </v-list-item>
              
              <v-list-item 
                v-if="doc.status === 'completed'"
                @click.stop="viewRecords(doc)"
              >
                <template v-slot:prepend>
                  <v-icon size="small">mdi-database</v-icon>
                </template>
                <v-list-item-title>View Records</v-list-item-title>
              </v-list-item>
              
              <v-divider></v-divider>
              
              <v-list-item @click.stop="deleteDocument(doc)" class="delete-item">
                <template v-slot:prepend>
                  <v-icon size="small" color="error">mdi-delete</v-icon>
                </template>
                <v-list-item-title class="text-error">Delete</v-list-item-title>
              </v-list-item>
            </v-list>
          </v-menu>
        </div>
      </div>
    </div>

    <!-- Document Details Dialog -->
    <v-dialog v-model="detailsDialog" max-width="700">
      <v-card class="details-dialog-premium">
        <v-card-title class="dialog-header">
          <v-icon left color="primary">mdi-file-document</v-icon>
          Document Details
          <v-spacer></v-spacer>
          <v-btn icon @click="detailsDialog = false">
            <v-icon>mdi-close</v-icon>
          </v-btn>
        </v-card-title>

        <v-card-text v-if="selectedDocument" class="dialog-content">
          <div class="detail-section">
            <h4 class="section-title">File Information</h4>
            <div class="detail-grid">
              <div class="detail-item">
                <span class="detail-label">File Name</span>
                <span class="detail-value">{{ selectedDocument.file_name }}</span>
              </div>
              <div class="detail-item">
                <span class="detail-label">File Size</span>
                <span class="detail-value">{{ formatFileSize(selectedDocument.file_size) }}</span>
              </div>
              <div class="detail-item">
                <span class="detail-label">Document Type</span>
                <span class="detail-value">{{ selectedDocument.document_type }}</span>
              </div>
              <div class="detail-item">
                <span class="detail-label">Processing Mode</span>
                <span class="detail-value">{{ selectedDocument.processing_mode || 'Professional' }}</span>
              </div>
            </div>
          </div>

          <v-divider class="my-4"></v-divider>

          <div class="detail-section">
            <h4 class="section-title">Processing Status</h4>
            <div class="detail-grid">
              <div class="detail-item">
                <span class="detail-label">Status</span>
                <div class="status-badge" :class="getStatusClass(selectedDocument.status)">
                  <div class="status-dot"></div>
                  <span>{{ selectedDocument.status }}</span>
                </div>
              </div>
              <div class="detail-item">
                <span class="detail-label">Records Processed</span>
                <span class="detail-value">{{ selectedDocument.records_processed || 0 }}</span>
              </div>
              <div class="detail-item">
                <span class="detail-label">Total Records</span>
                <span class="detail-value">{{ selectedDocument.total_records || '-' }}</span>
              </div>
              <div class="detail-item">
                <span class="detail-label">Created At</span>
                <span class="detail-value">{{ formatDate(selectedDocument.created_at) }}</span>
              </div>
            </div>
          </div>

          <v-divider class="my-4"></v-divider>

          <div class="detail-section" v-if="selectedDocument.metadata">
            <h4 class="section-title">Metadata</h4>
            <div class="detail-grid">
              <div class="detail-item" v-if="selectedDocument.metadata.bank_name">
                <span class="detail-label">Bank/Client</span>
                <span class="detail-value">{{ selectedDocument.metadata.bank_name }}</span>
              </div>
              <div class="detail-item" v-if="selectedDocument.metadata.product">
                <span class="detail-label">Product</span>
                <span class="detail-value">{{ selectedDocument.metadata.product }}</span>
              </div>
              <div class="detail-item" v-if="selectedDocument.metadata.rfp_name">
                <span class="detail-label">RFP Name</span>
                <span class="detail-value">{{ selectedDocument.metadata.rfp_name }}</span>
              </div>
            </div>
          </div>
        </v-card-text>

        <v-card-actions class="dialog-actions">
          <v-btn
            v-if="selectedDocument?.status === 'completed'"
            class="action-btn-emerald"
            @click="viewRecords(selectedDocument)"
          >
            <v-icon left>mdi-database</v-icon>
            View Records
          </v-btn>
          <v-spacer></v-spacer>
          <v-btn
            class="action-btn-error"
            @click="deleteDocument(selectedDocument); detailsDialog = false"
          >
            <v-icon left>mdi-delete</v-icon>
            Delete
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'DocumentsEnhanced',
  data() {
    return {
      documents: [],
      loading: false,
      search: '',
      filterStatus: 'All',
      filterType: 'All',
      viewMode: 'grid',
      detailsDialog: false,
      selectedDocument: null,
      statusFilters: ['All', 'completed', 'processing', 'failed', 'awaiting_mapping', 'uploaded'],
      typeFilters: ['All', 'RFP', 'Documentation']
    }
  },
  computed: {
    filteredDocuments() {
      let filtered = this.documents

      // Search filter
      if (this.search) {
        const searchLower = this.search.toLowerCase()
        filtered = filtered.filter(doc => 
          doc.file_name.toLowerCase().includes(searchLower) ||
          doc.metadata?.bank_name?.toLowerCase().includes(searchLower) ||
          doc.metadata?.product?.toLowerCase().includes(searchLower)
        )
      }

      // Status filter
      if (this.filterStatus && this.filterStatus !== 'All') {
        filtered = filtered.filter(doc => doc.status === this.filterStatus)
      }

      // Type filter
      if (this.filterType && this.filterType !== 'All') {
        filtered = filtered.filter(doc => doc.document_type === this.filterType)
      }

      return filtered
    },
    completedCount() {
      return this.documents.filter(doc => doc.status === 'completed').length
    },
    processingCount() {
      return this.documents.filter(doc => doc.status === 'processing' || doc.status === 'awaiting_mapping').length
    },
    failedCount() {
      return this.documents.filter(doc => doc.status === 'failed').length
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
        const response = await axios.get(`${API_URL}/documents`, {
          params: { sort_by: 'created_at', sort_order: 'desc' }
        })
        
        if (response.data && Array.isArray(response.data.documents)) {
          this.documents = response.data.documents.map(doc => ({
            ...doc,
            id: doc._id
          }))
        }
      } catch (error) {
        console.error('Error loading documents:', error)
        this.$toast?.error('Failed to load documents')
      } finally {
        this.loading = false
      }
    },
    async deleteDocument(document) {
      if (confirm(`Are you sure you want to delete "${document.file_name}"? This action cannot be undone.`)) {
        try {
          const API_URL = process.env.VUE_APP_API_URL || 'http://localhost:5000/api'
          const documentId = document._id || document.id
          
          const response = await axios.delete(`${API_URL}/documents/${documentId}`)
          
          if (response.status === 200) {
            this.$toast?.success('Document deleted successfully')
            // Remove from local array immediately for better UX
            const index = this.documents.findIndex(d => (d._id || d.id) === documentId)
            if (index !== -1) {
              this.documents.splice(index, 1)
            }
            // Reload to ensure consistency
            await this.loadDocuments()
          }
        } catch (error) {
          console.error('Delete error:', error)
          const errorMsg = error.response?.data?.error || 'Failed to delete document'
          this.$toast?.error(errorMsg)
        }
      }
    },
    viewDocument(doc) {
      this.selectedDocument = doc
      this.detailsDialog = true
    },
    viewRecords(doc) {
      this.$router.push(`/search?document_id=${doc._id || doc.id}`)
    },
    getFileIcon(filename) {
      const ext = filename.split('.').pop().toLowerCase()
      const iconMap = {
        'xlsx': 'mdi-microsoft-excel',
        'xls': 'mdi-microsoft-excel',
        'pdf': 'mdi-file-pdf-box',
        'docx': 'mdi-file-word-box',
        'doc': 'mdi-file-word-box'
      }
      return iconMap[ext] || 'mdi-file-document'
    },
    getFileTypeClass(filename) {
      const ext = filename.split('.').pop().toLowerCase()
      if (ext === 'xlsx' || ext === 'xls') return 'excel'
      if (ext === 'pdf') return 'pdf'
      if (ext === 'docx' || ext === 'doc') return 'word'
      return 'default'
    },
    getStatusClass(status) {
      const classMap = {
        'completed': 'status-completed',
        'processing': 'status-processing',
        'failed': 'status-failed',
        'awaiting_mapping': 'status-awaiting',
        'uploaded': 'status-uploaded'
      }
      return classMap[status] || 'status-default'
    },
    formatDate(dateStr) {
      if (!dateStr) return '-'
      const date = new Date(dateStr)
      return date.toLocaleDateString('en-US', { 
        month: 'short', 
        day: 'numeric', 
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      })
    },
    formatFileSize(bytes) {
      if (!bytes) return '-'
      if (bytes < 1024) return bytes + ' B'
      if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
      return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
    }
  }
}
</script>

<style scoped>
/* Premium Color Palette */
:root {
  --emerald-from: #047857;
  --emerald-to: #059669;
  --gold-from: #D97706;
  --gold-to: #F59E0B;
  --navy-from: #0F172A;
  --navy-to: #1E293B;
  --slate: #64748B;
}

.documents-container-premium {
  font-family: 'Poppins', 'Inter', sans-serif;
  padding: 32px;
  max-width: 1400px;
  margin: 0 auto;
  background: linear-gradient(135deg, #F8FAFC 0%, #F1F5F9 100%);
  min-height: 100vh;
}

/* Premium Header */
.premium-header {
  margin-bottom: 32px;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.title-section {
  display: flex;
  align-items: center;
  gap: 20px;
}

.icon-badge {
  width: 64px;
  height: 64px;
  background: linear-gradient(135deg, var(--emerald-from), var(--emerald-to));
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 20px rgba(4, 120, 87, 0.3);
}

.page-title {
  font-family: 'Poppins', sans-serif;
  font-size: 2rem;
  font-weight: 700;
  background: linear-gradient(135deg, var(--navy-from), var(--navy-to));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin: 0;
}

.page-subtitle {
  font-size: 0.95rem;
  color: #64748B;
  margin: 4px 0 0;
}

.upload-btn-premium {
  background: linear-gradient(135deg, var(--emerald-from), var(--emerald-to)) !important;
  color: white !important;
  text-transform: none !important;
  font-weight: 600 !important;
  padding: 12px 32px !important;
  height: 48px !important;
  box-shadow: 0 4px 16px rgba(4, 120, 87, 0.3) !important;
  transition: all 0.3s ease !important;
}

.upload-btn-premium:hover {
  background: linear-gradient(135deg, var(--gold-from), var(--gold-to)) !important;
  box-shadow: 0 6px 24px rgba(217, 119, 6, 0.5) !important;
  transform: translateY(-2px);
}

/* Stats Grid */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
}

.stat-card-premium {
  background: white;
  border-radius: 16px;
  padding: 24px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
  border: 2px solid transparent;
}

.stat-card-premium:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
}

.stat-card-premium.emerald .stat-icon {
  background: linear-gradient(135deg, var(--emerald-from), var(--emerald-to));
}

.stat-card-premium.emerald:hover {
  border-color: var(--emerald-to);
}

.stat-card-premium.gold .stat-icon {
  background: linear-gradient(135deg, var(--gold-from), var(--gold-to));
}

.stat-card-premium.gold:hover {
  border-color: var(--gold-to);
}

.stat-card-premium.navy .stat-icon {
  background: linear-gradient(135deg, var(--navy-from), var(--navy-to));
}

.stat-card-premium.navy:hover {
  border-color: var(--navy-to);
}

.stat-card-premium.slate .stat-icon {
  background: linear-gradient(135deg, #475569, #64748B);
}

.stat-card-premium.slate:hover {
  border-color: #64748B;
}

.stat-icon {
  width: 56px;
  height: 56px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.stat-details {
  flex: 1;
}

.stat-value {
  font-size: 2rem;
  font-weight: 700;
  color: #0F172A;
  line-height: 1;
}

.stat-label {
  font-size: 0.875rem;
  color: #64748B;
  margin-top: 4px;
}

/* Filters Section */
.filters-section {
  display: flex;
  gap: 16px;
  margin-bottom: 24px;
  flex-wrap: wrap;
}

.search-field-premium,
.filter-select-premium {
  background: white;
  border-radius: 12px;
}

.search-field-premium {
  flex: 2;
  min-width: 250px;
}

.filter-select-premium {
  flex: 1;
  min-width: 180px;
}

/* View Toggle */
.view-toggle {
  display: flex;
  justify-content: flex-end;
  margin-bottom: 16px;
}

.toggle-premium {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

/* Loading & Empty States */
.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 20px;
  gap: 20px;
}

.loading-text {
  font-size: 1.1rem;
  color: #64748B;
}

.empty-state-premium {
  background: white;
  border-radius: 20px;
  padding: 80px 40px;
  text-align: center;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
}

.empty-icon {
  margin-bottom: 24px;
}

.empty-title {
  font-size: 1.75rem;
  font-weight: 700;
  color: #0F172A;
  margin-bottom: 8px;
}

.empty-subtitle {
  font-size: 1.1rem;
  color: #64748B;
  margin-bottom: 32px;
}

/* Documents Grid */
.documents-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 24px;
}

.document-card-premium {
  background: white;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
  cursor: pointer;
  border: 2px solid transparent;
}

.document-card-premium:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 28px rgba(0, 0, 0, 0.15);
  border-color: var(--emerald-to);
}

.card-header {
  padding: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #E2E8F0;
}

.file-icon-wrapper {
  width: 56px;
  height: 56px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.file-icon-wrapper.excel {
  background: linear-gradient(135deg, #107C41, #33A853);
}

.file-icon-wrapper.pdf {
  background: linear-gradient(135deg, #DC2626, #EF4444);
}

.file-icon-wrapper.word {
  background: linear-gradient(135deg, #1E40AF, #3B82F6);
}

.file-icon-wrapper.default {
  background: linear-gradient(135deg, #64748B, #94A3B8);
}

.menu-btn {
  opacity: 0.7;
  transition: opacity 0.2s;
}

.document-card-premium:hover .menu-btn {
  opacity: 1;
}

.card-body {
  padding: 20px;
}

.doc-title {
  font-size: 1.1rem;
  font-weight: 600;
  color: #0F172A;
  margin-bottom: 12px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.doc-metadata {
  display: flex;
  gap: 16px;
  margin-bottom: 12px;
}

.metadata-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 0.85rem;
  color: #64748B;
}

.metadata-icon {
  color: #94A3B8;
}

.doc-info {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 16px;
  min-height: 28px;
}

.info-chip {
  display: flex;
  align-items: center;
  background: #F1F5F9;
  padding: 4px 12px;
  border-radius: 6px;
  font-size: 0.75rem;
  color: #475569;
  font-weight: 500;
}

.doc-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 16px;
  border-top: 1px solid #F1F5F9;
}

.status-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  border-radius: 8px;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: capitalize;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  animation: pulse 2s ease-in-out infinite;
}

.status-completed {
  background: #D1FAE5;
  color: #047857;
}

.status-completed .status-dot {
  background: #047857;
}

.status-processing {
  background: #FEF3C7;
  color: #D97706;
}

.status-processing .status-dot {
  background: #D97706;
}

.status-failed {
  background: #FEE2E2;
  color: #DC2626;
}

.status-failed .status-dot {
  background: #DC2626;
}

.status-awaiting {
  background: #DBEAFE;
  color: #1E40AF;
}

.status-awaiting .status-dot {
  background: #1E40AF;
}

.status-uploaded {
  background: #F3F4F6;
  color: #6B7280;
}

.status-uploaded .status-dot {
  background: #6B7280;
}

.doc-date {
  font-size: 0.75rem;
  color: #94A3B8;
}

/* List View */
.documents-list {
  background: white;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.list-header {
  display: flex;
  padding: 20px 24px;
  background: linear-gradient(135deg, #F8FAFC, #F1F5F9);
  border-bottom: 2px solid #E2E8F0;
  font-weight: 600;
  color: #475569;
  font-size: 0.875rem;
}

.list-header-cell {
  padding: 0 12px;
}

.list-row-premium {
  display: flex;
  padding: 20px 24px;
  border-bottom: 1px solid #F1F5F9;
  transition: all 0.2s ease;
  cursor: pointer;
  align-items: center;
}

.list-row-premium:hover {
  background: linear-gradient(135deg, #F8FAFC, #F1F5F9);
  border-left: 4px solid var(--emerald-to);
}

.list-cell {
  padding: 0 12px;
  display: flex;
  align-items: center;
}

.file-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.file-icon-small {
  width: 40px;
  height: 40px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.file-icon-small.excel {
  background: linear-gradient(135deg, #107C41, #33A853);
}

.file-icon-small.pdf {
  background: linear-gradient(135deg, #DC2626, #EF4444);
}

.file-icon-small.word {
  background: linear-gradient(135deg, #1E40AF, #3B82F6);
}

.file-icon-small.default {
  background: linear-gradient(135deg, #64748B, #94A3B8);
}

.file-details {
  min-width: 0;
}

.file-name {
  font-weight: 600;
  color: #0F172A;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-size: 0.95rem;
}

.file-size {
  font-size: 0.75rem;
  color: #94A3B8;
  margin-top: 2px;
}

.type-badge {
  background: #F1F5F9;
  padding: 6px 12px;
  border-radius: 6px;
  font-size: 0.75rem;
  font-weight: 600;
  color: #475569;
}

.records-count {
  font-size: 0.875rem;
  color: #64748B;
  font-weight: 500;
}

.date-text {
  font-size: 0.875rem;
  color: #64748B;
}

/* Dialog */
.details-dialog-premium {
  border-radius: 20px !important;
  overflow: hidden;
}

.dialog-header {
  background: linear-gradient(135deg, var(--navy-from), var(--navy-to));
  color: white !important;
  padding: 24px !important;
  font-family: 'Poppins', sans-serif;
  font-size: 1.25rem;
  font-weight: 600;
}

.dialog-content {
  padding: 32px 24px !important;
}

.detail-section {
  margin-bottom: 24px;
}

.section-title {
  font-size: 1.1rem;
  font-weight: 600;
  color: #0F172A;
  margin-bottom: 16px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.detail-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
}

.detail-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.detail-label {
  font-size: 0.75rem;
  font-weight: 600;
  color: #94A3B8;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.detail-value {
  font-size: 0.95rem;
  color: #0F172A;
  font-weight: 500;
}

.dialog-actions {
  padding: 20px 24px !important;
  background: #F8FAFC;
}

.action-btn-emerald {
  background: linear-gradient(135deg, var(--emerald-from), var(--emerald-to)) !important;
  color: white !important;
  text-transform: none !important;
  font-weight: 600 !important;
  padding: 8px 20px !important;
}

.action-btn-error {
  background: linear-gradient(135deg, #DC2626, #EF4444) !important;
  color: white !important;
  text-transform: none !important;
  font-weight: 600 !important;
  padding: 8px 20px !important;
}

/* Menu */
.menu-list-premium {
  border-radius: 12px !important;
  overflow: hidden;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15) !important;
}

.delete-item:hover {
  background: #FEE2E2 !important;
}

/* Animations */
@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

/* Responsive */
@media (max-width: 768px) {
  .documents-container-premium {
    padding: 16px;
  }

  .header-content {
    flex-direction: column;
    gap: 16px;
    align-items: flex-start;
  }

  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .filters-section {
    flex-direction: column;
  }

  .search-field-premium,
  .filter-select-premium {
    width: 100%;
  }

  .documents-grid {
    grid-template-columns: 1fr;
  }

  .list-header {
    display: none;
  }

  .list-row-premium {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }

  .list-cell {
    width: 100%;
    padding: 4px 12px;
  }
}
</style>
