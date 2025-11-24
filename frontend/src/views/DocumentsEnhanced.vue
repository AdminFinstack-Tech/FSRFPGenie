<template>
  <div class="documents-container">
    <!-- Animated Header -->
    <div class="documents-header mb-8">
      <div class="header-gradient">
        <div class="header-content">
          <v-icon size="64" class="header-icon">mdi-folder-multiple</v-icon>
          <h1 class="display-1 font-weight-bold">Documents Library</h1>
          <p class="subtitle-1">Manage, search, and organize your uploaded documents</p>
        </div>
      </div>
    </div>

    <!-- Quick Stats -->
    <v-row class="mb-6">
      <v-col cols="12" md="3" v-for="(stat, index) in stats" :key="index">
        <v-card class="stat-card" :style="`animation-delay: ${index * 0.1}s`">
          <div class="stat-icon-wrapper" :class="stat.color">
            <v-icon color="white" size="32">{{ stat.icon }}</v-icon>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ stat.value }}</div>
            <div class="stat-label">{{ stat.label }}</div>
          </div>
        </v-card>
      </v-col>
    </v-row>

    <!-- Toolbar -->
    <v-card class="mb-4 toolbar-card">
      <v-card-text class="pa-4">
        <v-row align="center">
          <!-- Search -->
          <v-col cols="12" md="4">
            <v-text-field
              v-model="searchQuery"
              placeholder="Search documents..."
              prepend-inner-icon="mdi-magnify"
              variant="outlined"
              density="compact"
              hide-details
              clearable
            ></v-text-field>
          </v-col>

          <!-- Filters -->
          <v-col cols="12" md="6">
            <div class="d-flex gap-2">
              <v-select
                v-model="selectedType"
                :items="documentTypes"
                placeholder="All Types"
                variant="outlined"
                density="compact"
                hide-details
                clearable
                style="max-width: 200px;"
              >
                <template v-slot:prepend-inner>
                  <v-icon size="20">mdi-filter</v-icon>
                </template>
              </v-select>

              <v-select
                v-model="selectedStatus"
                :items="statusOptions"
                placeholder="All Status"
                variant="outlined"
                density="compact"
                hide-details
                clearable
                style="max-width: 200px;"
              >
                <template v-slot:prepend-inner>
                  <v-icon size="20">mdi-chart-donut</v-icon>
                </template>
              </v-select>

              <v-menu offset-y>
                <template v-slot:activator="{ props }">
                  <v-btn
                    v-bind="props"
                    variant="outlined"
                    density="compact"
                  >
                    <v-icon left size="20">mdi-calendar</v-icon>
                    Date Range
                  </v-btn>
                </template>
                <v-list dense>
                  <v-list-item @click="setDateRange('today')">Today</v-list-item>
                  <v-list-item @click="setDateRange('week')">This Week</v-list-item>
                  <v-list-item @click="setDateRange('month')">This Month</v-list-item>
                  <v-list-item @click="setDateRange('all')">All Time</v-list-item>
                </v-list>
              </v-menu>
            </div>
          </v-col>

          <!-- View Mode & Actions -->
          <v-col cols="12" md="2" class="text-right">
            <div class="d-flex justify-end gap-2">
              <v-btn-toggle v-model="viewMode" mandatory density="compact">
                <v-btn value="grid" size="small">
                  <v-icon>mdi-view-grid</v-icon>
                </v-btn>
                <v-btn value="list" size="small">
                  <v-icon>mdi-view-list</v-icon>
                </v-btn>
                <v-btn value="compact" size="small">
                  <v-icon>mdi-view-comfy</v-icon>
                </v-btn>
              </v-btn-toggle>
            </div>
          </v-col>
        </v-row>

        <!-- Bulk Actions Bar -->
        <v-slide-y-transition>
          <div v-if="selectedDocuments.length > 0" class="bulk-actions-bar mt-4">
            <div class="d-flex align-center">
              <v-checkbox
                :model-value="allSelected"
                @update:model-value="toggleSelectAll"
                hide-details
                density="compact"
                class="mr-2"
              ></v-checkbox>
              <span class="font-weight-medium">{{ selectedDocuments.length }} selected</span>
              <v-spacer></v-spacer>
              <v-btn
                variant="text"
                color="primary"
                size="small"
                @click="bulkReprocess"
                class="mr-2"
              >
                <v-icon left size="20">mdi-refresh</v-icon>
                Reprocess
              </v-btn>
              <v-btn
                variant="text"
                color="info"
                size="small"
                @click="bulkExport"
                class="mr-2"
              >
                <v-icon left size="20">mdi-download</v-icon>
                Export
              </v-btn>
              <v-btn
                variant="text"
                color="error"
                size="small"
                @click="bulkDelete"
              >
                <v-icon left size="20">mdi-delete</v-icon>
                Delete
              </v-btn>
            </div>
          </div>
        </v-slide-y-transition>
      </v-card-text>
    </v-card>

    <!-- Grid View -->
    <v-row v-if="viewMode === 'grid' && !loading">
      <v-col
        v-for="doc in filteredDocuments"
        :key="doc.id"
        cols="12"
        md="4"
        lg="3"
      >
        <v-card
          class="document-card"
          :class="{ selected: isSelected(doc.id) }"
          @click="toggleSelect(doc.id)"
        >
          <!-- Selection Checkbox -->
          <div class="selection-overlay">
            <v-checkbox
              :model-value="isSelected(doc.id)"
              hide-details
              density="compact"
              @click.stop="toggleSelect(doc.id)"
            ></v-checkbox>
          </div>

          <!-- File Icon -->
          <div class="file-icon-container" :style="`background: ${getFileColor(doc.file_name)}`">
            <v-icon color="white" size="48">{{ getFileIcon(doc.file_name) }}</v-icon>
            <div class="file-extension">{{ getFileExtension(doc.file_name).toUpperCase() }}</div>
          </div>

          <!-- Document Info -->
          <v-card-text>
            <div class="document-title">{{ doc.file_name }}</div>
            <div class="document-meta">
              <v-chip size="x-small" variant="flat" class="mr-1">
                {{ formatFileSize(doc.file_size) }}
              </v-chip>
              <v-chip
                size="x-small"
                :color="getStatusColor(doc.status)"
                variant="flat"
              >
                {{ doc.status }}
              </v-chip>
            </div>
            <div class="document-date">
              <v-icon size="14">mdi-clock-outline</v-icon>
              {{ formatDate(doc.created_at) }}
            </div>
            <div v-if="doc.records_processed" class="document-progress mt-2">
              <div class="progress-label">
                {{ doc.records_processed }} / {{ doc.total_records || '?' }} records
              </div>
              <v-progress-linear
                :model-value="getProcessingProgress(doc)"
                :color="getStatusColor(doc.status)"
                height="4"
                rounded
              ></v-progress-linear>
            </div>
          </v-card-text>

          <!-- Actions -->
          <v-card-actions>
            <v-btn
              size="small"
              variant="text"
              color="primary"
              @click.stop="viewDocument(doc)"
            >
              <v-icon left size="18">mdi-eye</v-icon>
              View
            </v-btn>
            <v-spacer></v-spacer>
            <v-menu offset-y>
              <template v-slot:activator="{ props }">
                <v-btn
                  v-bind="props"
                  icon
                  size="small"
                  variant="text"
                  @click.stop
                >
                  <v-icon>mdi-dots-vertical</v-icon>
                </v-btn>
              </template>
              <v-list dense>
                <v-list-item @click="downloadDocument(doc)">
                  <v-list-item-title>
                    <v-icon left size="18">mdi-download</v-icon>
                    Download
                  </v-list-item-title>
                </v-list-item>
                <v-list-item @click="reprocessDocument(doc)">
                  <v-list-item-title>
                    <v-icon left size="18">mdi-refresh</v-icon>
                    Reprocess
                  </v-list-item-title>
                </v-list-item>
                <v-divider></v-divider>
                <v-list-item @click="deleteDocument(doc)">
                  <v-list-item-title class="error--text">
                    <v-icon left size="18" color="error">mdi-delete</v-icon>
                    Delete
                  </v-list-item-title>
                </v-list-item>
              </v-list>
            </v-menu>
          </v-card-actions>
        </v-card>
      </v-col>
    </v-row>

    <!-- List View -->
    <v-card v-if="viewMode === 'list' && !loading" class="list-view-card">
      <v-data-table
        v-model="selectedDocuments"
        :headers="listHeaders"
        :items="filteredDocuments"
        :items-per-page="15"
        show-select
        item-value="id"
      >
        <template v-slot:[`item.file_name`]="{ item }">
          <div class="d-flex align-center py-2">
            <div class="file-icon-small mr-3" :style="`background: ${getFileColor(item.file_name)}`">
              <v-icon color="white" size="20">{{ getFileIcon(item.file_name) }}</v-icon>
            </div>
            <div>
              <div class="font-weight-medium">{{ item.file_name }}</div>
              <div class="text-caption text-grey">{{ item.document_type }}</div>
            </div>
          </div>
        </template>

        <template v-slot:[`item.status`]="{ item }">
          <v-chip
            :color="getStatusColor(item.status)"
            size="small"
            variant="flat"
          >
            <v-icon v-if="item.status === 'processing'" left size="14" class="spin">
              mdi-loading
            </v-icon>
            {{ item.status }}
          </v-chip>
        </template>

        <template v-slot:[`item.records`]="{ item }">
          <div v-if="item.records_processed">
            <div class="text-caption">{{ item.records_processed }} / {{ item.total_records || '?' }}</div>
            <v-progress-linear
              :model-value="getProcessingProgress(item)"
              :color="getStatusColor(item.status)"
              height="4"
              rounded
              class="mt-1"
            ></v-progress-linear>
          </div>
          <span v-else>-</span>
        </template>

        <template v-slot:[`item.file_size`]="{ item }">
          {{ formatFileSize(item.file_size) }}
        </template>

        <template v-slot:[`item.created_at`]="{ item }">
          {{ formatDate(item.created_at, true) }}
        </template>

        <template v-slot:[`item.actions`]="{ item }">
          <v-btn
            icon
            size="small"
            variant="text"
            @click="viewDocument(item)"
          >
            <v-icon>mdi-eye</v-icon>
          </v-btn>
          <v-menu offset-y>
            <template v-slot:activator="{ props }">
              <v-btn
                v-bind="props"
                icon
                size="small"
                variant="text"
              >
                <v-icon>mdi-dots-vertical</v-icon>
              </v-btn>
            </template>
            <v-list dense>
              <v-list-item @click="downloadDocument(item)">
                <v-list-item-title>Download</v-list-item-title>
              </v-list-item>
              <v-list-item @click="reprocessDocument(item)">
                <v-list-item-title>Reprocess</v-list-item-title>
              </v-list-item>
              <v-divider></v-divider>
              <v-list-item @click="deleteDocument(item)">
                <v-list-item-title class="error--text">Delete</v-list-item-title>
              </v-list-item>
            </v-list>
          </v-menu>
        </template>
      </v-data-table>
    </v-card>

    <!-- Compact View -->
    <v-card v-if="viewMode === 'compact' && !loading" class="compact-view-card">
      <v-list>
        <v-list-item
          v-for="doc in filteredDocuments"
          :key="doc.id"
          class="compact-item"
          :class="{ selected: isSelected(doc.id) }"
          @click="toggleSelect(doc.id)"
        >
          <template v-slot:prepend>
            <v-checkbox
              :model-value="isSelected(doc.id)"
              hide-details
              density="compact"
              @click.stop="toggleSelect(doc.id)"
            ></v-checkbox>
            <div class="file-icon-mini mr-3" :style="`background: ${getFileColor(doc.file_name)}`">
              <v-icon color="white" size="16">{{ getFileIcon(doc.file_name) }}</v-icon>
            </div>
          </template>

          <v-list-item-title>{{ doc.file_name }}</v-list-item-title>
          <v-list-item-subtitle>
            {{ formatFileSize(doc.file_size) }} • {{ formatDate(doc.created_at) }}
          </v-list-item-subtitle>

          <template v-slot:append>
            <v-chip
              :color="getStatusColor(doc.status)"
              size="x-small"
              variant="flat"
              class="mr-2"
            >
              {{ doc.status }}
            </v-chip>
            <v-btn
              icon
              size="small"
              variant="text"
              @click.stop="viewDocument(doc)"
            >
              <v-icon>mdi-eye</v-icon>
            </v-btn>
          </template>
        </v-list-item>
      </v-list>
    </v-card>

    <!-- Loading State -->
    <div v-if="loading" class="text-center py-12">
      <v-progress-circular
        indeterminate
        color="primary"
        size="64"
      ></v-progress-circular>
      <p class="mt-4 text-grey">Loading documents...</p>
    </div>

    <!-- Empty State -->
    <v-card v-if="!loading && filteredDocuments.length === 0" class="empty-state-card">
      <v-card-text class="text-center py-12">
        <v-icon size="80" color="grey-lighten-1">mdi-folder-open-outline</v-icon>
        <h3 class="text-h6 mt-4 mb-2">No Documents Found</h3>
        <p class="text-grey mb-4">{{ searchQuery ? 'Try adjusting your filters' : 'Get started by uploading your first document' }}</p>
        <v-btn color="primary" @click="$router.push('/upload')">
          <v-icon left>mdi-upload</v-icon>
          Upload Document
        </v-btn>
      </v-card-text>
    </v-card>

    <!-- Document Preview Dialog -->
    <v-dialog v-model="previewDialog" max-width="800">
      <v-card v-if="selectedDocument">
        <v-card-title class="d-flex align-center">
          <v-icon :color="getFileColor(selectedDocument.file_name)" class="mr-2">
            {{ getFileIcon(selectedDocument.file_name) }}
          </v-icon>
          <span>{{ selectedDocument.file_name }}</span>
          <v-spacer></v-spacer>
          <v-btn icon variant="text" @click="previewDialog = false">
            <v-icon>mdi-close</v-icon>
          </v-btn>
        </v-card-title>

        <v-divider></v-divider>

        <v-card-text class="pa-6">
          <!-- Document Info Grid -->
          <v-row>
            <v-col cols="6">
              <div class="info-item">
                <div class="info-label">Type</div>
                <div class="info-value">{{ selectedDocument.document_type }}</div>
              </div>
            </v-col>
            <v-col cols="6">
              <div class="info-item">
                <div class="info-label">Status</div>
                <v-chip
                  :color="getStatusColor(selectedDocument.status)"
                  size="small"
                  variant="flat"
                >
                  {{ selectedDocument.status }}
                </v-chip>
              </div>
            </v-col>
            <v-col cols="6">
              <div class="info-item">
                <div class="info-label">File Size</div>
                <div class="info-value">{{ formatFileSize(selectedDocument.file_size) }}</div>
              </div>
            </v-col>
            <v-col cols="6">
              <div class="info-item">
                <div class="info-label">Uploaded</div>
                <div class="info-value">{{ formatDate(selectedDocument.created_at, true) }}</div>
              </div>
            </v-col>
            <v-col cols="6" v-if="selectedDocument.records_processed">
              <div class="info-item">
                <div class="info-label">Records Processed</div>
                <div class="info-value">
                  {{ selectedDocument.records_processed }} / {{ selectedDocument.total_records || '?' }}
                </div>
              </div>
            </v-col>
            <v-col cols="6" v-if="selectedDocument.processing_time">
              <div class="info-item">
                <div class="info-label">Processing Time</div>
                <div class="info-value">{{ selectedDocument.processing_time }}s</div>
              </div>
            </v-col>
          </v-row>

          <!-- Metadata -->
          <div v-if="selectedDocument.metadata && Object.keys(selectedDocument.metadata).length" class="mt-6">
            <h4 class="text-subtitle-2 font-weight-bold mb-3">Metadata</h4>
            <div class="metadata-grid">
              <v-chip
                v-for="(value, key) in selectedDocument.metadata"
                :key="key"
                size="small"
                variant="outlined"
                class="ma-1"
              >
                <strong>{{ key }}:</strong>&nbsp;{{ value }}
              </v-chip>
            </div>
          </div>

          <!-- Processing Progress -->
          <div v-if="selectedDocument.status === 'processing'" class="mt-6">
            <h4 class="text-subtitle-2 font-weight-bold mb-3">Processing Progress</h4>
            <v-progress-linear
              :model-value="getProcessingProgress(selectedDocument)"
              color="primary"
              height="8"
              rounded
            ></v-progress-linear>
            <p class="text-caption text-center mt-2">
              {{ getProcessingProgress(selectedDocument) }}% complete
            </p>
          </div>
        </v-card-text>

        <v-divider></v-divider>

        <v-card-actions class="pa-4">
          <v-btn
            variant="outlined"
            @click="downloadDocument(selectedDocument)"
          >
            <v-icon left>mdi-download</v-icon>
            Download
          </v-btn>
          <v-btn
            variant="outlined"
            color="primary"
            @click="reprocessDocument(selectedDocument)"
          >
            <v-icon left>mdi-refresh</v-icon>
            Reprocess
          </v-btn>
          <v-spacer></v-spacer>
          <v-btn
            variant="outlined"
            color="error"
            @click="deleteDocument(selectedDocument)"
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
import { format, isToday, isThisWeek, isThisMonth } from 'date-fns'

export default {
  name: 'DocumentsEnhanced',
  data() {
    return {
      loading: false,
      documents: [],
      selectedDocuments: [],
      searchQuery: '',
      selectedType: null,
      selectedStatus: null,
      dateRange: 'all',
      viewMode: 'grid',
      previewDialog: false,
      selectedDocument: null,
      pollingInterval: null,
      documentTypes: ['RFP', 'Documentation'],
      statusOptions: ['Processing', 'Completed', 'Failed', 'Awaiting Mapping'],
      listHeaders: [
        { title: 'File Name', value: 'file_name', sortable: true },
        { title: 'Status', value: 'status', sortable: true },
        { title: 'Records', value: 'records', sortable: false },
        { title: 'Size', value: 'file_size', sortable: true },
        { title: 'Uploaded', value: 'created_at', sortable: true },
        { title: 'Actions', value: 'actions', sortable: false, align: 'center' }
      ],
      stats: [
        { icon: 'mdi-file-multiple', value: '0', label: 'Total Documents', color: 'primary' },
        { icon: 'mdi-check-circle', value: '0', label: 'Completed', color: 'success' },
        { icon: 'mdi-progress-clock', value: '0', label: 'Processing', color: 'warning' },
        { icon: 'mdi-alert-circle', value: '0', label: 'Failed', color: 'error' }
      ]
    }
  },
  computed: {
    filteredDocuments() {
      let filtered = [...this.documents]

      // Search filter
      if (this.searchQuery) {
        const query = this.searchQuery.toLowerCase()
        filtered = filtered.filter(doc =>
          doc.file_name.toLowerCase().includes(query) ||
          (doc.metadata && JSON.stringify(doc.metadata).toLowerCase().includes(query))
        )
      }

      // Type filter
      if (this.selectedType) {
        filtered = filtered.filter(doc => doc.document_type === this.selectedType)
      }

      // Status filter
      if (this.selectedStatus) {
        filtered = filtered.filter(doc => doc.status === this.selectedStatus)
      }

      // Date range filter
      if (this.dateRange !== 'all') {
        filtered = filtered.filter(doc => {
          const date = new Date(doc.created_at)
          if (this.dateRange === 'today') return isToday(date)
          if (this.dateRange === 'week') return isThisWeek(date)
          if (this.dateRange === 'month') return isThisMonth(date)
          return true
        })
      }

      return filtered
    },
    allSelected() {
      return this.selectedDocuments.length === this.filteredDocuments.length &&
             this.filteredDocuments.length > 0
    }
  },
  mounted() {
    this.loadDocuments()
    this.pollingInterval = setInterval(this.loadDocuments, 10000)
  },
  beforeUnmount() {
    if (this.pollingInterval) {
      clearInterval(this.pollingInterval)
    }
  },
  methods: {
    async loadDocuments() {
      this.loading = true
      try {
        const API_URL = process.env.VUE_APP_API_URL || 'http://localhost:5000/api'
        const response = await axios.get(`${API_URL}/documents`, {
          params: { page: 1, limit: 100 }
        })

        this.documents = response.data.documents || []
        this.updateStats()
      } catch (error) {
        console.error('Failed to load documents:', error)
        this.documents = []
      } finally {
        this.loading = false
      }
    },
    updateStats() {
      this.stats[0].value = this.documents.length.toString()
      this.stats[1].value = this.documents.filter(d => d.status === 'completed').length.toString()
      this.stats[2].value = this.documents.filter(d => d.status === 'processing').length.toString()
      this.stats[3].value = this.documents.filter(d => d.status === 'failed').length.toString()
    },
    isSelected(docId) {
      return this.selectedDocuments.includes(docId)
    },
    toggleSelect(docId) {
      const index = this.selectedDocuments.indexOf(docId)
      if (index > -1) {
        this.selectedDocuments.splice(index, 1)
      } else {
        this.selectedDocuments.push(docId)
      }
    },
    toggleSelectAll() {
      if (this.allSelected) {
        this.selectedDocuments = []
      } else {
        this.selectedDocuments = this.filteredDocuments.map(d => d.id)
      }
    },
    setDateRange(range) {
      this.dateRange = range
    },
    viewDocument(doc) {
      this.selectedDocument = doc
      this.previewDialog = true
    },
    async downloadDocument(doc) {
      console.log('Downloading:', doc.file_name)
      // Implement download logic
    },
    async reprocessDocument(doc) {
      console.log('Reprocessing:', doc.file_name)
      // Implement reprocess logic
    },
    async deleteDocument(doc) {
      if (confirm(`Delete ${doc.file_name}?`)) {
        console.log('Deleting:', doc.file_name)
        this.loadDocuments()
      }
    },
    async bulkReprocess() {
      console.log('Bulk reprocess:', this.selectedDocuments)
    },
    async bulkExport() {
      console.log('Bulk export:', this.selectedDocuments)
    },
    async bulkDelete() {
      if (confirm(`Delete ${this.selectedDocuments.length} documents?`)) {
        console.log('Bulk delete:', this.selectedDocuments)
        this.selectedDocuments = []
        this.loadDocuments()
      }
    },
    getFileExtension(filename) {
      return filename.split('.').pop().toLowerCase()
    },
    getFileIcon(filename) {
      const ext = this.getFileExtension(filename)
      const icons = {
        xlsx: 'mdi-microsoft-excel',
        xls: 'mdi-microsoft-excel',
        xlsm: 'mdi-microsoft-excel',
        pdf: 'mdi-file-pdf-box',
        docx: 'mdi-microsoft-word',
        doc: 'mdi-microsoft-word'
      }
      return icons[ext] || 'mdi-file'
    },
    getFileColor(filename) {
      const ext = this.getFileExtension(filename)
      const colors = {
        xlsx: 'linear-gradient(135deg, #1e7e34, #28a745)',
        xls: 'linear-gradient(135deg, #1e7e34, #28a745)',
        xlsm: 'linear-gradient(135deg, #1e7e34, #28a745)',
        pdf: 'linear-gradient(135deg, #c82333, #dc3545)',
        docx: 'linear-gradient(135deg, #0056b3, #007bff)',
        doc: 'linear-gradient(135deg, #0056b3, #007bff)'
      }
      return colors[ext] || 'linear-gradient(135deg, #6c757d, #adb5bd)'
    },
    getStatusColor(status) {
      const colors = {
        'processing': 'warning',
        'completed': 'success',
        'failed': 'error',
        'awaiting_mapping': 'info'
      }
      return colors[status.toLowerCase()] || 'default'
    },
    getProcessingProgress(doc) {
      if (!doc.total_records || !doc.records_processed) return 0
      return Math.round((doc.records_processed / doc.total_records) * 100)
    },
    formatFileSize(bytes) {
      if (!bytes) return '0 B'
      const k = 1024
      const sizes = ['B', 'KB', 'MB', 'GB']
      const i = Math.floor(Math.log(bytes) / Math.log(k))
      return `${(bytes / Math.pow(k, i)).toFixed(1)} ${sizes[i]}`
    },
    formatDate(dateString, includeTime = false) {
      if (!dateString) return 'N/A'
      const date = new Date(dateString)
      return includeTime
        ? format(date, 'MMM dd, yyyy HH:mm')
        : format(date, 'MMM dd, yyyy')
    }
  }
}
</script>

<style scoped>
.documents-container {
  max-width: 1600px;
  margin: 0 auto;
  padding: 24px;
}

/* Header */
.documents-header {
  border-radius: 16px;
  overflow: hidden;
  margin-bottom: 32px;
}

.header-gradient {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 48px 32px;
  position: relative;
}

.header-content {
  position: relative;
  z-index: 1;
  text-align: center;
  color: white;
}

.header-icon {
  animation: float 3s ease-in-out infinite;
  margin-bottom: 16px;
}

/* Stats Cards */
.stat-card {
  display: flex;
  align-items: center;
  padding: 20px;
  border-radius: 12px;
  transition: all 0.3s ease;
  animation: slideInUp 0.5s ease-out;
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0,0,0,0.12);
}

.stat-icon-wrapper {
  width: 56px;
  height: 56px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 16px;
}

.stat-icon-wrapper.primary {
  background: linear-gradient(135deg, #667eea, #764ba2);
}

.stat-icon-wrapper.success {
  background: linear-gradient(135deg, #11998e, #38ef7d);
}

.stat-icon-wrapper.warning {
  background: linear-gradient(135deg, #f093fb, #f5576c);
}

.stat-icon-wrapper.error {
  background: linear-gradient(135deg, #ff6b6b, #c92a2a);
}

.stat-content {
  flex: 1;
}

.stat-value {
  font-size: 24px;
  font-weight: 700;
  color: #1a202c;
}

.stat-label {
  font-size: 14px;
  color: #718096;
}

/* Toolbar */
.toolbar-card {
  border-radius: 12px;
}

.bulk-actions-bar {
  padding: 16px;
  background: linear-gradient(135deg, #f7fafc 0%, #edf2f7 100%);
  border-radius: 8px;
  border: 2px solid #e2e8f0;
}

/* Grid View */
.document-card {
  border-radius: 12px;
  transition: all 0.3s ease;
  position: relative;
  cursor: pointer;
  animation: fadeInScale 0.4s ease-out;
}

.document-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 32px rgba(0,0,0,0.15);
}

.document-card.selected {
  border: 2px solid #667eea;
  box-shadow: 0 8px 24px rgba(102, 126, 234, 0.3);
}

.selection-overlay {
  position: absolute;
  top: 12px;
  right: 12px;
  z-index: 10;
}

.file-icon-container {
  height: 180px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  position: relative;
}

.file-extension {
  position: absolute;
  bottom: 12px;
  background: rgba(255,255,255,0.3);
  color: white;
  padding: 4px 12px;
  border-radius: 16px;
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  backdrop-filter: blur(10px);
}

.document-title {
  font-size: 14px;
  font-weight: 600;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  margin-bottom: 8px;
}

.document-meta {
  margin-bottom: 8px;
}

.document-date {
  font-size: 12px;
  color: #718096;
  display: flex;
  align-items: center;
  gap: 4px;
}

.document-progress {
  margin-top: 12px;
}

.progress-label {
  font-size: 11px;
  color: #718096;
  margin-bottom: 4px;
}

/* List View */
.file-icon-small {
  width: 40px;
  height: 40px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

/* Compact View */
.compact-item {
  border-bottom: 1px solid #e2e8f0;
  transition: background 0.2s ease;
}

.compact-item:hover {
  background: #f7fafc;
}

.compact-item.selected {
  background: #edf2f7;
}

.file-icon-mini {
  width: 32px;
  height: 32px;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* Preview Dialog */
.info-item {
  margin-bottom: 16px;
}

.info-label {
  font-size: 12px;
  font-weight: 600;
  color: #718096;
  text-transform: uppercase;
  margin-bottom: 4px;
}

.info-value {
  font-size: 14px;
  font-weight: 500;
  color: #1a202c;
}

.metadata-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

/* Empty State */
.empty-state-card {
  border-radius: 12px;
  background: linear-gradient(135deg, #f7fafc 0%, #edf2f7 100%);
}

/* Animations */
@keyframes slideInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes fadeInScale {
  from {
    opacity: 0;
    transform: scale(0.95);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

@keyframes float {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-10px);
  }
}

.spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

/* Responsive */
@media (max-width: 960px) {
  .documents-container {
    padding: 16px;
  }

  .header-gradient {
    padding: 32px 16px;
  }
}
</style>
