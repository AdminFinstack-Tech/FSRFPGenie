<template>
  <div>
    <!-- Page Header -->
    <div class="mb-8">
      <h1 class="text-3xl font-bold text-gray-900 mb-2">Documents</h1>
      <p class="text-gray-600">Manage uploaded documents and view processing status</p>
    </div>

    <!-- Documents Table -->
    <v-card>
      <v-data-table
        :headers="headers"
        :items="documents"
        :loading="loading"
        :items-per-page="15"
        class="elevation-0"
      >
        <!-- Custom header -->
        <template #top>
          <v-toolbar flat>
            <v-toolbar-title class="text-h6">All Documents</v-toolbar-title>
            <v-spacer></v-spacer>
            <v-btn color="primary" @click="$router.push('/upload')">
              <v-icon left>mdi-plus</v-icon>
              Upload New
            </v-btn>
          </v-toolbar>
        </template>

        <!-- Custom columns -->
        <template v-slot:[`item.file_name`]="{ item }">
          <div class="d-flex align-center py-2">
            <v-icon class="mr-2">{{ getFileIcon(item.file_name) }}</v-icon>
            <div>
              <div class="font-weight-medium">{{ item.file_name }}</div>
              <div class="text-caption text-gray-600">{{ formatFileSize(item.file_size) }}</div>
            </div>
          </div>
        </template>

        <template v-slot:[`item.document_type`]="{ item }">
          <v-chip small label>{{ item.document_type }}</v-chip>
        </template>

        <template v-slot:[`item.status`]="{ item }">
          <v-chip
            :color="getStatusColor(item.status)"
            dark
            small
            label
          >
            <v-icon left x-small v-if="item.status === 'processing'">
              mdi-loading mdi-spin
            </v-icon>
            {{ item.status }}
          </v-chip>
        </template>

        <template v-slot:[`item.records`]="{ item }">
          <span v-if="item.records_processed !== null">
            {{ item.records_processed }} / {{ item.total_records || '-' }}
          </span>
          <span v-else>-</span>
        </template>

        <template v-slot:[`item.created_at`]="{ item }">
          {{ formatDate(item.created_at) }}
        </template>

        <template v-slot:[`item.actions`]="{ item }">
          <v-menu offset-y>
            <template v-slot:activator="{ on, attrs }">
              <v-btn
                icon
                v-bind="attrs"
                v-on="on"
              >
                <v-icon>mdi-dots-vertical</v-icon>
              </v-btn>
            </template>
            <v-list dense>
              <v-list-item @click="viewDocument(item)">
                <v-list-item-icon>
                  <v-icon small>mdi-eye</v-icon>
                </v-list-item-icon>
                <v-list-item-title>View Details</v-list-item-title>
              </v-list-item>
              
              <v-list-item 
                v-if="item.status === 'awaiting_mapping'"
                @click="$router.push(`/mapping/${item.id}`)"
              >
                <v-list-item-icon>
                  <v-icon small>mdi-table-edit</v-icon>
                </v-list-item-icon>
                <v-list-item-title>Map Columns</v-list-item-title>
              </v-list-item>
              
              <v-list-item 
                v-if="item.status === 'completed'"
                @click="viewRecords(item)"
              >
                <v-list-item-icon>
                  <v-icon small>mdi-database</v-icon>
                </v-list-item-icon>
                <v-list-item-title>View Records</v-list-item-title>
              </v-list-item>
              
              <v-divider></v-divider>
              
              <v-list-item @click="deleteDocument(item)">
                <v-list-item-icon>
                  <v-icon small color="error">mdi-delete</v-icon>
                </v-list-item-icon>
                <v-list-item-title class="error--text">Delete</v-list-item-title>
              </v-list-item>
            </v-list>
          </v-menu>
        </template>
      </v-data-table>
    </v-card>

    <!-- Document Details Dialog -->
    <v-dialog v-model="detailsDialog" max-width="600">
      <v-card v-if="selectedDocument">
        <v-card-title>
          <span class="text-h6">Document Details</span>
          <v-spacer></v-spacer>
          <v-btn icon @click="detailsDialog = false">
            <v-icon>mdi-close</v-icon>
          </v-btn>
        </v-card-title>
        
        <v-card-text>
          <v-simple-table>
            <template v-slot:default>
              <tbody>
                <tr>
                  <td class="font-weight-medium">File Name</td>
                  <td>{{ selectedDocument.file_name }}</td>
                </tr>
                <tr>
                  <td class="font-weight-medium">Document Type</td>
                  <td>{{ selectedDocument.document_type }}</td>
                </tr>
                <tr>
                  <td class="font-weight-medium">Status</td>
                  <td>
                    <v-chip
                      :color="getStatusColor(selectedDocument.status)"
                      dark
                      small
                      label
                    >
                      {{ selectedDocument.status }}
                    </v-chip>
                  </td>
                </tr>
                <tr>
                  <td class="font-weight-medium">File Size</td>
                  <td>{{ formatFileSize(selectedDocument.file_size) }}</td>
                </tr>
                <tr>
                  <td class="font-weight-medium">Uploaded</td>
                  <td>{{ formatDate(selectedDocument.created_at, true) }}</td>
                </tr>
                <tr v-if="selectedDocument.records_processed">
                  <td class="font-weight-medium">Records Processed</td>
                  <td>{{ selectedDocument.records_processed }}</td>
                </tr>
                <tr v-if="selectedDocument.error_details && selectedDocument.error_details.length">
                  <td class="font-weight-medium">Errors</td>
                  <td>
                    <v-chip small color="error" label>
                      {{ selectedDocument.error_details.length }} errors
                    </v-chip>
                  </td>
                </tr>
              </tbody>
            </template>
          </v-simple-table>
          
          <!-- Metadata -->
          <div v-if="selectedDocument.metadata && Object.keys(selectedDocument.metadata).length" class="mt-4">
            <h4 class="text-subtitle-2 font-weight-bold mb-2">Metadata</h4>
            <v-chip
              v-for="(value, key) in selectedDocument.metadata"
              :key="key"
              small
              label
              class="mr-2 mb-2"
            >
              {{ key }}: {{ value }}
            </v-chip>
          </div>
        </v-card-text>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
import axios from 'axios'
import { format } from 'date-fns'

export default {
  name: 'DocumentsView',
  data() {
    return {
      loading: false,
      documents: [],
      headers: [
        { text: 'File Name', value: 'file_name', sortable: true },
        { text: 'Type', value: 'document_type', sortable: true },
        { text: 'Status', value: 'status', sortable: true },
        { text: 'Records', value: 'records', sortable: false },
        { text: 'Uploaded', value: 'created_at', sortable: true },
        { text: 'Actions', value: 'actions', sortable: false, align: 'center' }
      ],
      detailsDialog: false,
      selectedDocument: null,
      pollingInterval: null
    }
  },
  mounted() {
    this.loadDocuments()
    // Poll for status updates
    this.pollingInterval = setInterval(this.loadDocuments, 5000)
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
          params: {
            page: 1,
            limit: 100
          }
        })
        
        this.documents = response.data.documents || []
      } catch (error) {
        console.error('Failed to load documents:', error)
        this.documents = []
      } finally {
        this.loading = false
      }
    },
    viewDocument(document) {
      this.selectedDocument = document
      this.detailsDialog = true
    },
    viewRecords(document) {
      // Navigate to records view
      this.$router.push(`/documents/${document.id}/records`)
    },
    async deleteDocument(document) {
      if (confirm(`Are you sure you want to delete "${document.file_name}"? This action cannot be undone.`)) {
        try {
          const API_URL = process.env.VUE_APP_API_URL || 'http://localhost:5000/api'
          const documentId = document._id || document.id
          
          const response = await axios.delete(`${API_URL}/documents/${documentId}`)
          
          if (response.status === 200) {
            this.$toast.success('Document deleted successfully')
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
          this.$toast.error(errorMsg)
        }
      }
    },
    getFileIcon(filename) {
      const ext = filename.split('.').pop().toLowerCase()
      const icons = {
        xlsx: 'mdi-microsoft-excel',
        xls: 'mdi-microsoft-excel',
        pdf: 'mdi-file-pdf-box',
        docx: 'mdi-microsoft-word'
      }
      return icons[ext] || 'mdi-file'
    },
    getStatusColor(status) {
      const colors = {
        processing: 'info',
        completed: 'success',
        failed: 'error',
        partial: 'warning',
        awaiting_mapping: 'orange'
      }
      return colors[status] || 'gray'
    },
    formatFileSize(bytes) {
      const sizes = ['Bytes', 'KB', 'MB', 'GB']
      if (bytes === 0) return '0 Bytes'
      const i = Math.floor(Math.log(bytes) / Math.log(1024))
      return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i]
    },
    formatDate(dateString, includeTime = false) {
      if (!dateString) return 'N/A'
      const formatString = includeTime ? 'MMM d, yyyy h:mm a' : 'MMM d, yyyy'
      return format(new Date(dateString), formatString)
    }
  }
}
</script>