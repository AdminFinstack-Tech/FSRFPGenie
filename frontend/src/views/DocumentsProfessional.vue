<template>
  <div class="documents-professional">
    <!-- Page Header -->
    <div class="page-header">
      <h1 class="page-title">Documents</h1>
      <p class="page-description">Manage and browse your uploaded RFP documents</p>
    </div>

    <!-- Controls Bar -->
    <div class="controls-bar">
      <!-- Search -->
      <div class="search-box">
        <v-icon size="20" color="#64748b">mdi-magnify</v-icon>
        <input 
          v-model="searchQuery" 
          type="text" 
          class="search-input"
          placeholder="Search documents..."
          @input="filterDocuments"
        />
      </div>

      <!-- Actions -->
      <div class="controls-actions">
        <button class="btn-secondary" @click="loadDocuments">
          <v-icon size="18" left color="#64748b">mdi-refresh</v-icon>
          Refresh
        </button>
        <router-link to="/upload" class="btn-primary">
          <v-icon size="18" left color="white">mdi-upload</v-icon>
          Upload New
        </router-link>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="loading-state">
      <v-progress-circular indeterminate color="#14b8a6" size="64"></v-progress-circular>
      <p class="loading-text">Loading documents...</p>
    </div>

    <!-- Empty State -->
    <div v-else-if="filteredDocuments.length === 0 && !loading" class="empty-state">
      <v-icon size="64" color="#cbd5e1">mdi-file-document-outline</v-icon>
      <p class="empty-title">No documents found</p>
      <p class="empty-subtitle">{{ searchQuery ? 'Try a different search' : 'Upload your first document to get started' }}</p>
      <router-link v-if="!searchQuery" to="/upload" class="btn-primary">
        <v-icon left color="white">mdi-upload</v-icon>
        Upload Document
      </router-link>
    </div>

    <!-- Documents Table -->
    <div v-else class="documents-table">
      <div class="table-header">
        <div class="table-cell cell-name">Document</div>
        <div class="table-cell cell-metadata">Metadata</div>
        <div class="table-cell cell-status">Status</div>
        <div class="table-cell cell-date">Uploaded</div>
        <div class="table-cell cell-actions">Actions</div>
      </div>

      <div class="table-body">
        <div v-for="doc in filteredDocuments" :key="doc.id" class="table-row">
          <!-- Document Name -->
          <div class="table-cell cell-name">
            <div class="doc-icon">
              <v-icon :color="getFileIconColor(doc.file_name)">
                {{ getFileIcon(doc.file_name) }}
              </v-icon>
            </div>
            <div class="doc-info">
              <div class="doc-name">{{ doc.file_name }}</div>
              <div class="doc-size">{{ formatFileSize(doc.file_size) }}</div>
            </div>
          </div>

          <!-- Metadata -->
          <div class="table-cell cell-metadata">
            <div v-if="doc.bank_name || doc.product || doc.rfp_name" class="metadata-list">
              <div v-if="doc.bank_name" class="metadata-item">
                <span class="metadata-label">Bank:</span>
                <span class="metadata-value">{{ doc.bank_name }}</span>
              </div>
              <div v-if="doc.product" class="metadata-item">
                <span class="metadata-label">Product:</span>
                <span class="metadata-value">{{ doc.product }}</span>
              </div>
              <div v-if="doc.rfp_name" class="metadata-item">
                <span class="metadata-label">RFP:</span>
                <span class="metadata-value">{{ doc.rfp_name }}</span>
              </div>
            </div>
            <span v-else class="metadata-empty">—</span>
          </div>

          <!-- Status -->
          <div class="table-cell cell-status">
            <span :class="['status-badge', `status-${doc.status}`]">
              {{ formatStatus(doc.status) }}
            </span>
            <div v-if="doc.records_processed" class="records-count">
              {{ doc.records_processed }} records
            </div>
          </div>

          <!-- Date -->
          <div class="table-cell cell-date">
            <div class="date-text">{{ formatDate(doc.created_at) }}</div>
            <div class="time-text">{{ formatTime(doc.created_at) }}</div>
          </div>

          <!-- Actions -->
          <div class="table-cell cell-actions">
            <!-- Map Columns button for awaiting_mapping status -->
            <button 
              v-if="doc.status === 'awaiting_mapping'"
              class="action-btn action-btn-map" 
              @click="mapColumns(doc)"
              title="Map Columns"
            >
              <v-icon size="18" color="#14b8a6">mdi-table-cog</v-icon>
            </button>
            <button 
              class="action-btn action-btn-view" 
              @click="viewDocument(doc)"
              title="View details"
            >
              <v-icon size="18" color="#14b8a6">mdi-eye</v-icon>
            </button>
            <button 
              class="action-btn action-btn-download" 
              @click="downloadDocument(doc)"
              title="Download"
            >
              <v-icon size="18" color="#14b8a6">mdi-download</v-icon>
            </button>
            <button 
              class="action-btn action-btn-delete" 
              @click="confirmDelete(doc)"
              title="Delete"
            >
              <v-icon size="18" color="#ef4444">mdi-delete</v-icon>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Delete Confirmation Dialog -->
    <div v-if="showDeleteDialog" class="dialog-overlay" @click="showDeleteDialog = false">
      <div class="dialog-box" @click.stop>
        <div class="dialog-header">
          <h3 class="dialog-title">Delete Document</h3>
        </div>
        <div class="dialog-body">
          <p>Are you sure you want to delete <strong>{{ documentToDelete?.file_name }}</strong>?</p>
          <p class="dialog-warning">This action cannot be undone.</p>
        </div>
        <div class="dialog-actions">
          <button class="btn-secondary" @click="showDeleteDialog = false">Cancel</button>
          <button class="btn-danger" @click="deleteDocument">Delete</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'DocumentsProfessional',
  data() {
    return {
      loading: true,
      documents: [],
      filteredDocuments: [],
      searchQuery: '',
      showDeleteDialog: false,
      documentToDelete: null
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
        this.filteredDocuments = [...this.documents]
      } catch (error) {
        console.error('Error loading documents:', error)
      } finally {
        this.loading = false
      }
    },
    filterDocuments() {
      const query = this.searchQuery.toLowerCase()
      this.filteredDocuments = this.documents.filter(doc => 
        doc.file_name.toLowerCase().includes(query) ||
        doc.bank_name?.toLowerCase().includes(query) ||
        doc.product?.toLowerCase().includes(query) ||
        doc.rfp_name?.toLowerCase().includes(query)
      )
    },
    confirmDelete(doc) {
      this.documentToDelete = doc
      this.showDeleteDialog = true
    },
    async deleteDocument() {
      if (!this.documentToDelete) return

      try {
        const API_URL = process.env.VUE_APP_API_URL || 'http://localhost:5000/api'
        await axios.delete(`${API_URL}/documents/${this.documentToDelete.id}`)
        await this.loadDocuments()
        this.showDeleteDialog = false
        this.documentToDelete = null
      } catch (error) {
        console.error('Error deleting document:', error)
      }
    },
    mapColumns(doc) {
      this.$router.push(`/mapping/${doc.document_id}`)
    },
    viewDocument(doc) {
      this.$router.push(`/documents/${doc.id}`)
    },
    downloadDocument(doc) {
      if (doc.blob_url) {
        window.open(doc.blob_url, '_blank')
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
    formatStatus(status) {
      return status.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
    },
    formatDate(dateStr) {
      if (!dateStr) return 'Unknown'
      const date = new Date(dateStr)
      return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
    },
    formatTime(dateStr) {
      if (!dateStr) return ''
      const date = new Date(dateStr)
      return date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })
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
.documents-professional {
  --slate-50:  #f8fafc;
  --slate-100: #f1f5f9;
  --slate-200: #e2e8f0;
  --slate-300: #cbd5e1;
  --slate-400: #94a3b8;
  --slate-500: #64748b;
  --slate-600: #475569;
  --slate-700: #334155;
  --slate-900: #0f172a;
  --teal-500: #14b8a6;
  --teal-600: #0d9488;
}

.documents-professional {
  padding: 0;
}

/* === Page Header === */
.page-header {
  padding: 32px 0 24px 0;
  border-bottom: 1px solid var(--slate-200);
  margin-bottom: 24px;
}

.page-title {
  font-size: 24px;
  font-weight: 700;
  color: var(--slate-900);
  margin: 0 0 8px 0;
}

.page-description {
  font-size: 16px;
  color: var(--slate-600);
  margin: 0;
}

/* === Controls Bar === */
.controls-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
  margin-bottom: 24px;
}

.search-box {
  flex: 1;
  max-width: 400px;
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 16px;
  background-color: white;
  border: 1px solid var(--slate-300);
  border-radius: 8px;
  transition: all 0.2s ease;
}

.search-box:focus-within {
  border-color: var(--teal-500);
  box-shadow: 0 0 0 3px rgba(20, 184, 166, 0.1);
}

.search-input {
  flex: 1;
  border: none;
  outline: none;
  font-size: 14px;
  color: var(--slate-900);
  background: transparent;
}

.search-input::placeholder {
  color: var(--slate-400);
}

.controls-actions {
  display: flex;
  gap: 12px;
}

.btn-primary {
  background-color: var(--teal-500);
  color: white;
  border: none;
  border-radius: 6px;
  padding: 10px 20px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  text-decoration: none;
  display: flex;
  align-items: center;
  gap: 6px;
}

.btn-primary:hover {
  background-color: var(--teal-600);
}

.btn-secondary {
  background-color: white;
  color: var(--slate-700);
  border: 1px solid var(--slate-300);
  border-radius: 6px;
  padding: 10px 20px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  gap: 6px;
}

.btn-secondary:hover {
  background-color: var(--slate-50);
  border-color: var(--slate-400);
}

.btn-danger {
  background-color: #ef4444;
  color: white;
  border: none;
  border-radius: 6px;
  padding: 10px 20px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-danger:hover {
  background-color: #dc2626;
}

/* === States === */
.loading-state,
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 24px;
  text-align: center;
  background-color: white;
  border: 1px solid var(--slate-200);
  border-radius: 8px;
}

.loading-text {
  font-size: 16px;
  color: var(--slate-600);
  margin-top: 16px;
}

.empty-title {
  font-size: 18px;
  font-weight: 600;
  color: var(--slate-900);
  margin: 16px 0 8px 0;
}

.empty-subtitle {
  font-size: 14px;
  color: var(--slate-500);
  margin: 0 0 24px 0;
}

/* === Documents Table === */
.documents-table {
  background-color: white;
  border: 1px solid var(--slate-200);
  border-radius: 8px;
  overflow: hidden;
}

.table-header {
  display: grid;
  grid-template-columns: 2fr 1.5fr 1fr 1fr 120px;
  gap: 16px;
  padding: 16px 24px;
  background-color: var(--slate-50);
  border-bottom: 1px solid var(--slate-200);
  font-size: 12px;
  font-weight: 600;
  color: var(--slate-700);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.table-body {
  display: flex;
  flex-direction: column;
}

.table-row {
  display: grid;
  grid-template-columns: 2fr 1.5fr 1fr 1fr 120px;
  gap: 16px;
  padding: 16px 24px;
  border-bottom: 1px solid var(--slate-200);
  transition: background-color 0.2s ease;
}

.table-row:last-child {
  border-bottom: none;
}

.table-row:hover {
  background-color: var(--slate-50);
}

.table-cell {
  display: flex;
  align-items: center;
}

/* === Cell: Name === */
.cell-name {
  gap: 12px;
}

.doc-icon {
  width: 40px;
  height: 40px;
  background-color: var(--slate-50);
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.doc-info {
  flex: 1;
  min-width: 0;
}

.doc-name {
  font-size: 14px;
  font-weight: 500;
  color: var(--slate-900);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.doc-size {
  font-size: 12px;
  color: var(--slate-500);
  margin-top: 2px;
}

/* === Cell: Metadata === */
.metadata-list {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.metadata-item {
  font-size: 12px;
}

.metadata-label {
  color: var(--slate-500);
  font-weight: 500;
}

.metadata-value {
  color: var(--slate-700);
  margin-left: 4px;
}

.metadata-empty {
  color: var(--slate-400);
}

/* === Cell: Status === */
.cell-status {
  flex-direction: column;
  align-items: flex-start;
  gap: 4px;
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

.records-count {
  font-size: 11px;
  color: var(--slate-500);
}

/* === Cell: Date === */
.cell-date {
  flex-direction: column;
  align-items: flex-start;
  gap: 2px;
}

.date-text {
  font-size: 13px;
  color: var(--slate-700);
  font-weight: 500;
}

.time-text {
  font-size: 12px;
  color: var(--slate-500);
}

/* === Cell: Actions === */
.cell-actions {
  gap: 8px;
  justify-content: flex-end;
}

.action-btn {
  width: 32px;
  height: 32px;
  background-color: white;
  border: 1px solid var(--slate-200);
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s ease;
}

.action-btn:hover {
  background-color: var(--slate-50);
  border-color: var(--teal-500);
}

.action-btn-map {
  background-color: var(--teal-50);
  border-color: var(--teal-500);
}

.action-btn-map:hover {
  background-color: var(--teal-100);
}

.action-btn-delete:hover {
  background-color: #fef2f2;
  border-color: #ef4444;
}

/* === Dialog === */
.dialog-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.dialog-box {
  background-color: white;
  border-radius: 8px;
  width: 90%;
  max-width: 480px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
}

.dialog-header {
  padding: 20px 24px;
  border-bottom: 1px solid var(--slate-200);
}

.dialog-title {
  font-size: 18px;
  font-weight: 600;
  color: var(--slate-900);
  margin: 0;
}

.dialog-body {
  padding: 24px;
}

.dialog-body p {
  font-size: 14px;
  color: var(--slate-700);
  margin: 0 0 12px 0;
  line-height: 1.5;
}

.dialog-warning {
  color: #991b1b;
  font-weight: 500;
}

.dialog-actions {
  padding: 16px 24px;
  border-top: 1px solid var(--slate-200);
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

/* === Responsive === */
@media (max-width: 1024px) {
  .table-header,
  .table-row {
    grid-template-columns: 2fr 1fr 1fr 100px;
  }
  
  .cell-metadata {
    display: none;
  }
}

@media (max-width: 768px) {
  .controls-bar {
    flex-direction: column;
    align-items: stretch;
  }
  
  .search-box {
    max-width: none;
  }
  
  .controls-actions {
    justify-content: stretch;
  }
  
  .btn-primary,
  .btn-secondary {
    flex: 1;
    justify-content: center;
  }
}
</style>
