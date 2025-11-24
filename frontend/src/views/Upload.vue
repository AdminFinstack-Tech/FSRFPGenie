<template>
  <div class="upload-container">
    <!-- Page Header with Icon -->
    <div class="mb-8 header-section">
      <div class="d-flex align-center mb-4">
        <v-icon size="48" color="primary" class="mr-4">mdi-cloud-upload</v-icon>
        <div>
          <h1 class="text-3xl font-bold text-gray-900 mb-1">Upload Documents</h1>
          <p class="text-gray-600">Add new RFP files or documentation to your knowledge base</p>
        </div>
      </div>
      
      <!-- Quick Stats -->
      <div class="stats-row">
        <div class="stat-card">
          <v-icon color="success" size="24">mdi-file-check</v-icon>
          <div class="stat-info">
            <div class="stat-value">{{ recentUploads.length }}</div>
            <div class="stat-label">Recent Uploads</div>
          </div>
        </div>
        <div class="stat-card">
          <v-icon color="primary" size="24">mdi-file-multiple</v-icon>
          <div class="stat-info">
            <div class="stat-value">All Types</div>
            <div class="stat-label">Supported Formats</div>
          </div>
        </div>
        <div class="stat-card">
          <v-icon color="warning" size="24">mdi-database</v-icon>
          <div class="stat-info">
            <div class="stat-value">50 MB</div>
            <div class="stat-label">Max File Size</div>
          </div>
        </div>
      </div>
    </div>

    <!-- Document Type Selection with Enhanced UI -->
    <v-card class="mb-6 pa-6 type-selector-card" elevation="2">
      <div class="d-flex align-center mb-4">
        <v-icon color="primary" class="mr-3">mdi-format-list-bulleted-type</v-icon>
        <h2 class="text-h6 font-weight-bold">Select Document Type</h2>
      </div>
      <v-radio-group v-model="documentType" row>
        <v-radio label="RFP Document" value="RFP" color="primary">
          <template v-slot:label>
            <div class="type-option">
              <v-icon left color="success">mdi-microsoft-excel</v-icon>
              <div>
                <div class="font-weight-medium">RFP Document</div>
                <div class="text-body-2 text-gray-600">Excel files (.xlsx, .xls) with requirements and responses</div>
              </div>
            </div>
          </template>
        </v-radio>
        <v-radio label="Application Documentation" value="Documentation" class="ml-8" color="primary">
          <template v-slot:label>
            <div class="type-option">
              <v-icon left color="info">mdi-file-document</v-icon>
              <div>
                <div class="font-weight-medium">Application Documentation</div>
                <div class="text-body-2 text-gray-600">PDF or DOCX reference materials</div>
              </div>
            </div>
          </template>
        </v-radio>
      </v-radio-group>
    </v-card>

    <!-- Processing Mode Selection -->
    <v-card v-if="documentType === 'RFP'" class="mb-6 pa-6 mode-selector-card" elevation="2">
      <div class="d-flex align-center mb-4">
        <v-icon color="primary" class="mr-3">mdi-cog-outline</v-icon>
        <h2 class="text-h6 font-weight-bold">Processing Mode</h2>
      </div>
      <v-radio-group v-model="processingMode" row>
        <v-radio label="Simple Mode" value="simple" color="success">
          <template v-slot:label>
            <div class="mode-option">
              <div class="mode-icon-wrapper simple-mode">
                <v-icon color="white" size="28">mdi-lightning-bolt</v-icon>
              </div>
              <div class="mode-content">
                <div class="font-weight-bold text-lg">Simple Mode</div>
                <div class="text-body-2 text-gray-600 mt-1">
                  One-click processing - Upload and search immediately without configuration
                </div>
                <div class="mode-features mt-2">
                  <v-chip size="x-small" color="success" variant="flat" class="mr-1">
                    <v-icon start size="12">mdi-check</v-icon>
                    Zero setup
                  </v-chip>
                  <v-chip size="x-small" color="success" variant="flat" class="mr-1">
                    <v-icon start size="12">mdi-check</v-icon>
                    Auto-process
                  </v-chip>
                  <v-chip size="x-small" color="success" variant="flat">
                    <v-icon start size="12">mdi-check</v-icon>
                    Fast
                  </v-chip>
                </div>
              </div>
            </div>
          </template>
        </v-radio>
        <v-radio label="Professional Mode" value="professional" class="ml-8" color="primary">
          <template v-slot:label>
            <div class="mode-option">
              <div class="mode-icon-wrapper professional-mode">
                <v-icon color="white" size="28">mdi-briefcase</v-icon>
              </div>
              <div class="mode-content">
                <div class="font-weight-bold text-lg">Professional Mode</div>
                <div class="text-body-2 text-gray-600 mt-1">
                  Structured processing - Map columns, categorize data, and enable advanced filtering
                </div>
                <div class="mode-features mt-2">
                  <v-chip size="x-small" color="primary" variant="flat" class="mr-1">
                    <v-icon start size="12">mdi-check</v-icon>
                    Column mapping
                  </v-chip>
                  <v-chip size="x-small" color="primary" variant="flat" class="mr-1">
                    <v-icon start size="12">mdi-check</v-icon>
                    Filters
                  </v-chip>
                  <v-chip size="x-small" color="primary" variant="flat">
                    <v-icon start size="12">mdi-check</v-icon>
                    Templates
                  </v-chip>
                </div>
              </div>
            </div>
          </template>
        </v-radio>
      </v-radio-group>
      
      <!-- Mode Info Alert -->
      <v-alert
        :type="processingMode === 'simple' ? 'success' : 'info'"
        variant="tonal"
        density="compact"
        class="mt-4"
      >
        <template v-slot:prepend>
          <v-icon>{{ processingMode === 'simple' ? 'mdi-information' : 'mdi-lightbulb-on' }}</v-icon>
        </template>
        <span v-if="processingMode === 'simple'">
          <strong>Simple Mode:</strong> Your file will be automatically processed without column mapping. 
          All rows will be embedded and indexed for semantic search immediately after upload.
        </span>
        <span v-else>
          <strong>Professional Mode:</strong> After upload, you'll map Excel columns to RFP fields 
          for structured data extraction and advanced filtering capabilities.
        </span>
      </v-alert>
    </v-card>

    <!-- Enhanced File Upload Area -->
    <v-card class="mb-6 upload-card" elevation="2">
      <v-card-text class="pa-0">
        <div
          class="upload-zone pa-12 text-center"
          :class="{ 'drag-over': isDragging, 'has-file': selectedFile }"
          @drop.prevent="handleDrop"
          @dragover.prevent="isDragging = true"
          @dragenter.prevent="isDragging = true"
          @dragleave.prevent="isDragging = false"
          @click="$refs.fileInput.click()"
        >
          <input
            ref="fileInput"
            type="file"
            :accept="acceptedFormats"
            @change="handleFileSelect"
            style="display: none"
            multiple="false"
          />
          
          <!-- Upload Icon with Animation -->
          <div class="upload-icon-wrapper mb-4">
            <v-icon 
              :size="isDragging ? 80 : 64" 
              :color="isDragging ? 'success' : 'primary'" 
              class="upload-icon"
            >
              {{ isDragging ? 'mdi-cloud-download' : 'mdi-cloud-upload-outline' }}
            </v-icon>
          </div>
          
          <h3 class="text-h5 font-weight-bold mb-2" :class="isDragging ? 'text-success' : ''">
            {{ isDragging ? '📥 Drop your file here' : '☁️ Drag and drop file here' }}
          </h3>
          
          <p class="text-body-1 text-gray-600 mb-4">
            or <span class="browse-link">click to browse files</span>
          </p>
          
          <!-- Accepted File Types -->
          <div class="mb-4">
            <v-chip-group>
              <v-chip color="success" variant="outlined" size="small">
                <v-icon left size="small">mdi-microsoft-excel</v-icon>
                Excel (.xlsx, .xls)
              </v-chip>
              <v-chip color="error" variant="outlined" size="small" v-if="documentType === 'Documentation'">
                <v-icon left size="small">mdi-file-pdf-box</v-icon>
                PDF
              </v-chip>
              <v-chip color="info" variant="outlined" size="small" v-if="documentType === 'Documentation'">
                <v-icon left size="small">mdi-microsoft-word</v-icon>
                DOCX
              </v-chip>
            </v-chip-group>
          </div>
          
          <v-divider class="my-4"></v-divider>
          
          <div class="text-caption text-gray-500">
            <v-icon size="16" class="mr-1">mdi-information</v-icon>
            Maximum file size: 50MB | Supported: {{ getSupportedFormats() }}
          </div>
        </div>
      </v-card-text>
    </v-card>

    <!-- Selected File & Metadata with Enhanced UI -->
    <v-card v-if="selectedFile" class="mb-6 pa-6 selected-file-card" elevation="3">
      <!-- File Preview Header -->
      <div class="file-preview-header mb-4">
        <div class="d-flex align-center">
          <div class="file-icon-large mr-4">
            <v-icon :color="getFileIconColor(selectedFile.name)" size="48">
              {{ getFileIcon(selectedFile.name) }}
            </v-icon>
          </div>
          <div class="flex-grow-1">
            <h3 class="text-h6 font-weight-bold mb-1">{{ selectedFile.name }}</h3>
            <div class="d-flex align-center text-body-2 text-gray-600">
              <v-chip size="x-small" color="info" class="mr-2">{{ formatFileSize(selectedFile.size) }}</v-chip>
              <v-chip size="x-small" color="success">{{ getFileExtension(selectedFile.name).toUpperCase() }}</v-chip>
            </div>
          </div>
          <v-btn 
            icon 
            variant="text" 
            @click="removeFile"
            color="error"
          >
            <v-icon>mdi-close-circle</v-icon>
          </v-btn>
        </div>
        
        <!-- Upload Progress (shown during upload) -->
        <v-progress-linear
          v-if="uploading"
          :model-value="uploadProgress"
          color="primary"
          height="6"
          rounded
          class="mt-4"
        ></v-progress-linear>
      </div>

      <!-- RFP Metadata -->
      <div v-if="documentType === 'RFP'">
        <v-divider class="mb-4"></v-divider>
        <h4 class="text-subtitle-1 font-weight-bold mb-3">RFP Information</h4>
        <v-row>
          <v-col cols="12" md="6">
            <v-text-field
              v-model="rfpMetadata.rfp_name"
              label="RFP Name"
              placeholder="e.g., ABC Bank Digital Transformation RFP 2025"
              required
              :rules="[v => !!v || 'RFP name is required']"
            ></v-text-field>
          </v-col>
          <v-col cols="12" md="6">
            <v-text-field
              v-model="rfpMetadata.bank_name"
              label="Bank/Client Name"
              placeholder="e.g., ABC Bank"
              required
              :rules="[v => !!v || 'Bank name is required']"
            ></v-text-field>
          </v-col>
          <v-col cols="12" md="6">
            <v-text-field
              v-model="rfpMetadata.product"
              label="Primary Product"
              placeholder="e.g., MLC, EPLC, Integration"
            ></v-text-field>
          </v-col>
        </v-row>
      </div>

      <!-- Documentation Metadata -->
      <div v-else>
        <v-divider class="mb-4"></v-divider>
        <h4 class="text-subtitle-1 font-weight-bold mb-3">Document Information</h4>
        <v-row>
          <v-col cols="12" md="6">
            <v-text-field
              v-model="docMetadata.document_name"
              label="Document Name"
              placeholder="e.g., Security Best Practices Guide"
              required
              :rules="[v => !!v || 'Document name is required']"
            ></v-text-field>
          </v-col>
          <v-col cols="12" md="6">
            <v-text-field
              v-model="docMetadata.related_product"
              label="Related Product"
              placeholder="e.g., EV7, CEV6"
              required
              :rules="[v => !!v || 'Related product is required']"
            ></v-text-field>
          </v-col>
          <v-col cols="12" md="6">
            <v-text-field
              v-model="docMetadata.submodule"
              label="Submodule (Optional)"
              placeholder="e.g., GAPI, Mobile"
            ></v-text-field>
          </v-col>
          <v-col cols="12" md="6">
            <v-select
              v-model="docMetadata.document_category"
              label="Document Category"
              :items="documentCategories"
              required
              :rules="[v => !!v || 'Document category is required']"
            ></v-select>
          </v-col>
          <v-col cols="12">
            <v-combobox
              v-model="docMetadata.tags"
              label="Tags"
              placeholder="Add tags..."
              multiple
              chips
              closable-chips
              clearable
              hint="Press Enter to add tags"
              persistent-hint
            ></v-combobox>
          </v-col>
        </v-row>
      </div>

      <!-- Upload Button with Better Styling -->
      <div class="mt-6 d-flex justify-space-between align-center">
        <v-btn
          variant="outlined"
          color="error"
          @click="removeFile"
          :disabled="uploading"
        >
          <v-icon left>mdi-delete</v-icon>
          Remove File
        </v-btn>
        
        <v-btn
          color="primary"
          size="large"
          @click="uploadFile"
          :loading="uploading"
          :disabled="!isValid || uploading"
          elevation="2"
        >
          <v-icon left>mdi-cloud-upload</v-icon>
          {{ uploading ? 'Uploading...' : 'Upload Document' }}
        </v-btn>
      </div>
    </v-card>

    <!-- Recent Uploads -->
    <v-card class="pa-6" v-if="recentUploads.length > 0">
      <h2 class="text-h6 font-weight-bold mb-4">Recent Uploads</h2>
      <v-list>
        <v-list-item
          v-for="upload in recentUploads"
          :key="upload.id"
          class="px-0"
        >
          <v-list-item-avatar>
            <v-icon>{{ getFileIcon(upload.file_name) }}</v-icon>
          </v-list-item-avatar>
          
          <v-list-item-content>
            <v-list-item-title>{{ upload.file_name }}</v-list-item-title>
            <v-list-item-subtitle>
              {{ upload.document_type }} • {{ formatDate(upload.created_at) }}
            </v-list-item-subtitle>
          </v-list-item-content>
          
          <v-list-item-action>
            <v-chip
              :color="getStatusColor(upload.status)"
              dark
              small
              label
            >
              {{ upload.status }}
            </v-chip>
          </v-list-item-action>
        </v-list-item>
      </v-list>
    </v-card>
  </div>
</template>

<script>
import { format } from 'date-fns'

export default {
  name: 'UploadView',
  data() {
    return {
      documentType: 'RFP',
      processingMode: 'simple', // 'simple' or 'professional'
      selectedFile: null,
      isDragging: false,
      uploading: false,
      uploadProgress: 0,
      rfpMetadata: {
        rfp_name: '',
        bank_name: '',
        product: ''
      },
      docMetadata: {
        document_name: '',
        related_product: '',
        submodule: '',
        document_category: '',
        tags: []
      },
      documentCategories: ['Guidance', 'White Paper', 'User Manual', 'Gap Document', 'Technical Specification', 'Best Practices'],
      recentUploads: []
    }
  },
  computed: {
    acceptedFormats() {
      // Support ALL file types
      return this.documentType === 'RFP' 
        ? '.xlsx,.xls,.xlsm' 
        : '.pdf,.docx,.doc'
    },
    isValid() {
      if (!this.selectedFile) return false
      
      if (this.documentType === 'RFP') {
        return this.rfpMetadata.rfp_name && this.rfpMetadata.bank_name
      } else {
        return this.docMetadata.document_name && 
               this.docMetadata.related_product && 
               this.docMetadata.document_category
      }
    }
  },
  mounted() {
    this.loadRecentUploads()
  },
  methods: {
    handleDrop(e) {
      e.preventDefault()
      e.stopPropagation()
      this.isDragging = false
      
      const files = e.dataTransfer?.files
      if (files && files.length > 0) {
        this.processFile(files[0])
      }
    },
    handleFileSelect(e) {
      const files = e.target?.files
      if (files && files.length > 0) {
        this.processFile(files[0])
      }
    },
    processFile(file) {
      // Validate file exists
      if (!file) {
        this.showToast('error', 'No file selected')
        return
      }
      
      // Validate file size (50MB)
      const maxSize = 50 * 1024 * 1024
      if (file.size > maxSize) {
        this.showToast('error', `File size exceeds 50MB limit. Your file is ${this.formatFileSize(file.size)}`)
        return
      }
      
      // Validate file type
      const extension = this.getFileExtension(file.name)
      const validExtensions = this.documentType === 'RFP' 
        ? ['xlsx', 'xls', 'xlsm'] 
        : ['pdf', 'docx', 'doc']
      
      if (!validExtensions.includes(extension)) {
        this.showToast('error', `Invalid file type "${extension}". Expected: ${validExtensions.join(', ')}`)
        return
      }
      
      this.selectedFile = file
      this.showToast('success', `File "${file.name}" selected successfully`)
    },
    removeFile() {
      this.selectedFile = null
      if (this.$refs.fileInput) {
        this.$refs.fileInput.value = ''
      }
      this.resetMetadata()
    },
    async uploadFile() {
      if (!this.selectedFile || !this.isValid) {
        this.showToast('warning', 'Please fill in all required fields')
        return
      }
      
      this.uploading = true
      this.uploadProgress = 0
      
      try {
        const metadata = this.documentType === 'RFP' 
          ? this.rfpMetadata 
          : this.docMetadata
        
        // Simulate progress
        const progressInterval = setInterval(() => {
          if (this.uploadProgress < 90) {
            this.uploadProgress += 10
          }
        }, 300)
        
        const response = await this.$store.dispatch('uploadDocument', {
          file: this.selectedFile,
          documentType: this.documentType,
          metadata,
          processingMode: this.processingMode // Include processing mode
        })
        
        clearInterval(progressInterval)
        this.uploadProgress = 100
        
        this.showToast('success', 'Document uploaded successfully!')
        
        // Handle routing based on mode
        if (this.documentType === 'RFP' && response.document_id) {
          if (this.processingMode === 'simple') {
            // Simple mode: Show success and redirect to documents page
            setTimeout(() => {
              this.showToast('info', 'Document processing in background. You can view it in Documents!')
              this.$router.push('/documents')
            }, 1500)
          } else {
            // Professional mode: Redirect to column mapping
            setTimeout(() => {
              this.$router.push(`/mapping/${response.document_id}`)
            }, 1000)
          }
        } else {
          // Reset form for documentation
          this.removeFile()
          this.loadRecentUploads()
        }
        
      } catch (error) {
        console.error('Upload error:', error)
        const errorMessage = error.response?.data?.error || error.message || 'Failed to upload document'
        this.showToast('error', errorMessage)
      } finally {
        this.uploading = false
        this.uploadProgress = 0
      }
    },
    resetMetadata() {
      this.rfpMetadata = {
        rfp_name: '',
        bank_name: '',
        product: ''
      }
      this.docMetadata = {
        document_name: '',
        related_product: '',
        submodule: '',
        document_category: '',
        tags: []
      }
    },
    async loadRecentUploads() {
      try {
        // Load recent uploads from backend or localStorage
        const stored = localStorage.getItem('recentUploads')
        if (stored) {
          this.recentUploads = JSON.parse(stored).slice(0, 5)
        }
      } catch (error) {
        console.error('Failed to load recent uploads:', error)
      }
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
      return icons[ext] || 'mdi-file-document'
    },
    getFileIconColor(filename) {
      const ext = this.getFileExtension(filename)
      const colors = {
        xlsx: 'success',
        xls: 'success',
        xlsm: 'success',
        pdf: 'error',
        docx: 'info',
        doc: 'info'
      }
      return colors[ext] || 'grey'
    },
    getFileExtension(filename) {
      if (!filename || typeof filename !== 'string') return ''
      return filename.split('.').pop().toLowerCase()
    },
    getSupportedFormats() {
      return this.documentType === 'RFP' 
        ? 'Excel (.xlsx, .xls, .xlsm)' 
        : 'PDF (.pdf), Word (.docx, .doc)'
    },
    formatFileSize(bytes) {
      if (!bytes || bytes === 0) return '0 Bytes'
      const sizes = ['Bytes', 'KB', 'MB', 'GB']
      const i = Math.floor(Math.log(bytes) / Math.log(1024))
      return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i]
    },
    formatDate(dateString) {
      if (!dateString) return 'N/A'
      try {
        return format(new Date(dateString), 'MMM d, yyyy h:mm a')
      } catch (error) {
        return dateString
      }
    },
    getStatusColor(status) {
      const colors = {
        processing: 'info',
        completed: 'success',
        failed: 'error',
        partial: 'warning',
        pending: 'orange'
      }
      return colors[status] || 'grey'
    },
    showToast(type, message) {
      // Safely handle toast notifications
      if (this.$toast && this.$toast[type]) {
        this.$toast[type](message)
      } else {
        console.log(`[${type.toUpperCase()}]`, message)
      }
    }
  }
}
</script>

<style scoped>
.upload-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.header-section {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 2rem;
  border-radius: 12px;
  color: white;
  box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
}

.header-section h1,
.header-section p,
.header-section .v-icon {
  color: white !important;
}

.stats-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin-top: 1.5rem;
}

.stat-card {
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(10px);
  padding: 1rem;
  border-radius: 8px;
  display: flex;
  align-items: center;
  gap: 1rem;
  transition: all 0.3s ease;
}

.stat-card:hover {
  background: rgba(255, 255, 255, 0.25);
  transform: translateY(-2px);
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 1.25rem;
  font-weight: bold;
  color: white;
}

.stat-label {
  font-size: 0.75rem;
  opacity: 0.9;
  color: white;
}

.type-selector-card {
  border-left: 4px solid #667eea;
  transition: all 0.3s ease;
}

.type-selector-card:hover {
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12) !important;
}

.type-option {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

/* Processing Mode Styles */
.mode-selector-card {
  border-left: 4px solid #10b981;
  transition: all 0.3s ease;
}

.mode-selector-card:hover {
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12) !important;
}

.mode-option {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
  padding: 0.5rem 0;
}

.mode-icon-wrapper {
  min-width: 56px;
  height: 56px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.mode-icon-wrapper.simple-mode {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
}

.mode-icon-wrapper.professional-mode {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.mode-content {
  flex: 1;
}

.mode-features {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.upload-card {
  overflow: hidden;
  transition: all 0.3s ease;
}

.upload-zone {
  border: 3px dashed #e5e7eb;
  border-radius: 16px;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  cursor: pointer;
  position: relative;
  background: linear-gradient(135deg, #f6f9fc 0%, #ffffff 100%);
}

.upload-zone:hover {
  border-color: #667eea;
  background: linear-gradient(135deg, #f0f4ff 0%, #ffffff 100%);
  box-shadow: 0 8px 24px rgba(102, 126, 234, 0.15);
  transform: translateY(-2px);
}

.upload-zone.drag-over {
  border-color: #10b981;
  background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%);
  box-shadow: 0 12px 32px rgba(16, 185, 129, 0.25);
  transform: scale(1.02);
}

.upload-zone.has-file {
  border-color: #10b981;
  border-style: solid;
}

.upload-icon-wrapper {
  transition: all 0.3s ease;
}

.upload-icon {
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

.upload-zone:hover .upload-icon {
  transform: translateY(-8px);
}

.upload-zone.drag-over .upload-icon {
  transform: scale(1.2) rotate(10deg);
}

.browse-link {
  color: #667eea;
  font-weight: 600;
  text-decoration: underline;
  cursor: pointer;
  transition: color 0.3s ease;
}

.browse-link:hover {
  color: #764ba2;
}

.selected-file-card {
  border-left: 4px solid #10b981;
  animation: slideIn 0.4s ease;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.file-preview-header {
  background: linear-gradient(135deg, #f9fafb 0%, #ffffff 100%);
  padding: 1.5rem;
  border-radius: 12px;
  margin: -1.5rem -1.5rem 1.5rem -1.5rem;
}

.file-icon-large {
  background: linear-gradient(135deg, #f0f4ff 0%, #e0e7ff 100%);
  padding: 1rem;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* Responsive Design */
@media (max-width: 768px) {
  .stats-row {
    grid-template-columns: 1fr;
  }
  
  .upload-zone {
    padding: 2rem 1rem !important;
  }
  
  .type-option {
    flex-direction: column;
    text-align: center;
  }
}

/* Animation for file upload progress */
.v-progress-linear {
  transition: all 0.3s ease;
}

/* Better chip styling */
.v-chip {
  font-weight: 500;
  transition: all 0.2s ease;
}

.v-chip:hover {
  transform: scale(1.05);
}

/* Smooth transitions for all cards */
.v-card {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.v-card:hover {
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.1) !important;
}
</style>