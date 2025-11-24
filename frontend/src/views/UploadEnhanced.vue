<template>
  <div class="upload-container">
    <!-- Animated Header -->
    <div class="upload-header mb-8">
      <div class="header-gradient">
        <div class="header-content">
          <v-icon size="64" class="header-icon">mdi-cloud-upload</v-icon>
          <h1 class="display-1 font-weight-bold">Upload Documents</h1>
          <p class="subtitle-1">Drag & drop files or click to browse - Support for Excel, PDF, DOCX</p>
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

    <!-- Document Type & Mode Selection -->
    <v-row class="mb-6">
      <v-col cols="12" md="6">
        <v-card class="selection-card">
          <v-card-title class="d-flex align-center">
            <v-icon color="primary" class="mr-2">mdi-file-document</v-icon>
            Document Type
          </v-card-title>
          <v-card-text>
            <div class="type-buttons">
              <v-btn
                :variant="documentType === 'RFP' ? 'flat' : 'outlined'"
                :color="documentType === 'RFP' ? 'primary' : 'default'"
                size="large"
                block
                class="mb-3"
                @click="documentType = 'RFP'"
              >
                <v-icon left>mdi-microsoft-excel</v-icon>
                RFP Document
                <v-chip size="x-small" color="success" class="ml-2" v-if="documentType === 'RFP'">Selected</v-chip>
              </v-btn>
              <v-btn
                :variant="documentType === 'Documentation' ? 'flat' : 'outlined'"
                :color="documentType === 'Documentation' ? 'info' : 'default'"
                size="large"
                block
                @click="documentType = 'Documentation'"
              >
                <v-icon left>mdi-file-pdf-box</v-icon>
                Documentation
                <v-chip size="x-small" color="info" class="ml-2" v-if="documentType === 'Documentation'">Selected</v-chip>
              </v-btn>
            </div>
          </v-card-text>
        </v-card>
      </v-col>

      <!-- Processing Mode selector hidden - Simple mode is always used -->
      <v-col v-if="false" cols="12" md="6">
        <v-card class="selection-card">
          <v-card-title class="d-flex align-center">
            <v-icon color="primary" class="mr-2">mdi-cog</v-icon>
            Processing Mode
          </v-card-title>
          <v-card-text>
            <div class="mode-buttons">
              <v-btn
                :variant="processingMode === 'simple' ? 'flat' : 'outlined'"
                :color="processingMode === 'simple' ? 'success' : 'default'"
                size="large"
                block
                class="mb-3"
                @click="processingMode = 'simple'"
              >
                <v-icon left>mdi-lightning-bolt</v-icon>
                Simple Mode
                <v-chip size="x-small" color="success" class="ml-2" v-if="processingMode === 'simple'">Active</v-chip>
              </v-btn>
              <v-btn
                :variant="processingMode === 'professional' ? 'flat' : 'outlined'"
                :color="processingMode === 'professional' ? 'warning' : 'default'"
                size="large"
                block
                @click="processingMode = 'professional'"
              >
                <v-icon left>mdi-briefcase</v-icon>
                Professional Mode
                <v-chip size="x-small" color="warning" class="ml-2" v-if="processingMode === 'professional'">Active</v-chip>
              </v-btn>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Enhanced Drag & Drop Zone -->
    <v-card
      class="upload-zone-card mb-6"
      :class="{ 'drag-active': isDragging, 'has-files': selectedFiles.length > 0 }"
      @drop.prevent="handleDrop"
      @dragover.prevent="isDragging = true"
      @dragenter.prevent="isDragging = true"
      @dragleave.prevent="isDragging = false"
      @click="!uploading ? $refs.fileInput.click() : null"
    >
      <input
        ref="fileInput"
        type="file"
        :accept="acceptedFormats"
        @change="handleFileSelect"
        style="display: none"
        multiple
      />

      <div class="upload-zone-content">
        <!-- Animated Icon -->
        <div class="upload-animation">
          <v-icon 
            :size="isDragging ? 120 : 80"
            :color="isDragging ? 'success' : 'primary'"
            class="upload-icon"
          >
            {{ isDragging ? 'mdi-cloud-download' : 'mdi-cloud-upload-outline' }}
          </v-icon>
          <div class="icon-circle" v-if="!isDragging"></div>
        </div>

        <!-- Main Text -->
        <h2 class="upload-title" :class="{ 'success--text': isDragging }">
          {{ isDragging ? '📥 Drop files here!' : '☁️ Drag & Drop Files' }}
        </h2>
        <p class="upload-subtitle">
          or <span class="browse-text">click to browse</span>
        </p>

        <!-- Supported Formats -->
        <div class="format-chips">
          <v-chip
            v-for="format in supportedFormats"
            :key="format.ext"
            :color="format.color"
            variant="outlined"
            size="small"
            class="ma-1"
          >
            <v-icon left size="16">{{ format.icon }}</v-icon>
            {{ format.ext }}
          </v-chip>
        </div>

        <!-- File Size Info -->
        <div class="upload-info">
          <v-icon size="18" color="grey">mdi-information-outline</v-icon>
          <span>Max file size: 50MB | Multiple files supported</span>
        </div>
      </div>
    </v-card>

    <!-- Selected Files Preview -->
    <div v-if="selectedFiles.length > 0" class="mb-6">
      <h3 class="text-h6 mb-4 d-flex align-center">
        <v-icon color="primary" class="mr-2">mdi-file-multiple</v-icon>
        Selected Files ({{ selectedFiles.length }})
        <v-spacer></v-spacer>
        <v-btn
          variant="text"
          color="error"
          size="small"
          @click="clearAllFiles"
          :disabled="uploading"
        >
          <v-icon left>mdi-delete-sweep</v-icon>
          Clear All
        </v-btn>
      </h3>

      <v-row>
        <v-col
          v-for="(file, index) in selectedFiles"
          :key="index"
          cols="12"
          md="6"
        >
          <v-card class="file-preview-card">
            <!-- File Header -->
            <div class="file-preview-header">
              <div class="file-icon-large" :style="`background: ${getFileColor(file.name)}`">
                <v-icon color="white" size="32">{{ getFileIcon(file.name) }}</v-icon>
              </div>
              <div class="file-info">
                <div class="file-name">{{ file.name }}</div>
                <div class="file-meta">
                  <v-chip size="x-small" color="info" class="mr-1">{{ formatFileSize(file.size) }}</v-chip>
                  <v-chip size="x-small" color="success">{{ getFileExtension(file.name).toUpperCase() }}</v-chip>
                </div>
              </div>
              <v-btn
                icon
                variant="text"
                color="error"
                size="small"
                @click="removeFile(index)"
                :disabled="uploading"
              >
                <v-icon>mdi-close</v-icon>
              </v-btn>
            </div>

            <!-- Upload Progress -->
            <div v-if="uploading && file.progress !== undefined" class="file-progress">
              <div class="progress-info">
                <span>{{ file.progress }}%</span>
                <span class="upload-speed" v-if="file.speed">{{ file.speed }}</span>
              </div>
              <v-progress-linear
                :model-value="file.progress"
                :color="file.progress === 100 ? 'success' : 'primary'"
                height="8"
                rounded
              ></v-progress-linear>
              <div class="progress-status">
                <span v-if="file.progress < 100">Uploading...</span>
                <span v-else class="success--text">
                  <v-icon size="16" color="success">mdi-check-circle</v-icon>
                  Upload complete
                </span>
              </div>
            </div>

            <!-- File Preview (Excel) -->
            <div v-if="isExcelFile(file.name) && file.preview" class="file-preview-data">
              <div class="preview-label">First 3 rows:</div>
              <div class="excel-preview">
                <div class="excel-row excel-header">
                  <div v-for="(header, idx) in file.preview.headers" :key="idx" class="excel-cell">
                    {{ header }}
                  </div>
                </div>
                <div v-for="(row, rowIdx) in file.preview.rows.slice(0, 3)" :key="rowIdx" class="excel-row">
                  <div v-for="(cell, cellIdx) in row" :key="cellIdx" class="excel-cell">
                    {{ cell }}
                  </div>
                </div>
              </div>
            </div>
          </v-card>
        </v-col>
      </v-row>
    </div>

    <!-- Metadata Form -->
    <v-card v-if="selectedFiles.length > 0" class="mb-6 metadata-card">
      <v-card-title class="d-flex align-center">
        <v-icon color="primary" class="mr-2">mdi-information</v-icon>
        Document Information
      </v-card-title>
      <v-card-text>
        <!-- RFP Metadata -->
        <div v-if="documentType === 'RFP'">
          <v-row>
            <v-col cols="12" md="6">
              <v-text-field
                v-model="rfpMetadata.rfp_name"
                label="RFP Name *"
                placeholder="e.g., ABC Bank Digital Transformation RFP 2025"
                variant="outlined"
                density="comfortable"
                :rules="[v => !!v || 'Required']"
              >
                <template v-slot:prepend-inner>
                  <v-icon color="primary">mdi-file-document</v-icon>
                </template>
              </v-text-field>
            </v-col>
            <v-col cols="12" md="6">
              <v-text-field
                v-model="rfpMetadata.bank_name"
                label="Bank/Client Name *"
                placeholder="e.g., ABC Bank"
                variant="outlined"
                density="comfortable"
                :rules="[v => !!v || 'Required']"
              >
                <template v-slot:prepend-inner>
                  <v-icon color="primary">mdi-bank</v-icon>
                </template>
              </v-text-field>
            </v-col>
            <v-col cols="12" md="6">
              <v-text-field
                v-model="rfpMetadata.product"
                label="Primary Product"
                placeholder="e.g., MLC, EPLC, Integration"
                variant="outlined"
                density="comfortable"
              >
                <template v-slot:prepend-inner>
                  <v-icon color="primary">mdi-package-variant</v-icon>
                </template>
              </v-text-field>
            </v-col>
          </v-row>
        </div>

        <!-- Documentation Metadata -->
        <div v-else>
          <v-row>
            <v-col cols="12" md="6">
              <v-text-field
                v-model="docMetadata.document_name"
                label="Document Name *"
                placeholder="e.g., Security Best Practices Guide"
                variant="outlined"
                density="comfortable"
                :rules="[v => !!v || 'Required']"
              >
                <template v-slot:prepend-inner>
                  <v-icon color="info">mdi-file-document</v-icon>
                </template>
              </v-text-field>
            </v-col>
            <v-col cols="12" md="6">
              <v-text-field
                v-model="docMetadata.related_product"
                label="Related Product *"
                placeholder="e.g., EV7, CEV6"
                variant="outlined"
                density="comfortable"
                :rules="[v => !!v || 'Required']"
              >
                <template v-slot:prepend-inner>
                  <v-icon color="info">mdi-package</v-icon>
                </template>
              </v-text-field>
            </v-col>
            <v-col cols="12" md="6">
              <v-select
                v-model="docMetadata.document_category"
                label="Document Category *"
                :items="documentCategories"
                variant="outlined"
                density="comfortable"
                :rules="[v => !!v || 'Required']"
              >
                <template v-slot:prepend-inner>
                  <v-icon color="info">mdi-folder</v-icon>
                </template>
              </v-select>
            </v-col>
            <v-col cols="12" md="6">
              <v-combobox
                v-model="docMetadata.tags"
                label="Tags"
                placeholder="Add tags..."
                variant="outlined"
                density="comfortable"
                multiple
                chips
                closable-chips
              >
                <template v-slot:prepend-inner>
                  <v-icon color="info">mdi-tag-multiple</v-icon>
                </template>
              </v-combobox>
            </v-col>
          </v-row>
        </div>
      </v-card-text>
    </v-card>

    <!-- Action Buttons -->
    <v-card v-if="selectedFiles.length > 0" class="action-card">
      <v-card-actions class="pa-4">
        <v-btn
          variant="outlined"
          color="error"
          size="large"
          @click="clearAllFiles"
          :disabled="uploading"
        >
          <v-icon left>mdi-cancel</v-icon>
          Cancel
        </v-btn>
        <v-spacer></v-spacer>
        <v-btn
          color="primary"
          size="large"
          @click="uploadFiles"
          :loading="uploading"
          :disabled="!isValid || uploading"
          elevation="4"
          class="upload-btn"
        >
          <v-icon left>mdi-cloud-upload</v-icon>
          {{ uploading ? 'Uploading...' : `Upload ${selectedFiles.length} File${selectedFiles.length > 1 ? 's' : ''}` }}
        </v-btn>
      </v-card-actions>
    </v-card>

    <!-- Upload History -->
    <v-card v-if="uploadHistory.length > 0" class="mt-8 history-card">
      <v-card-title class="d-flex align-center">
        <v-icon color="primary" class="mr-2">mdi-history</v-icon>
        Upload History
        <v-spacer></v-spacer>
        <v-chip size="small" color="info">{{ uploadHistory.length }} uploads</v-chip>
      </v-card-title>
      <v-card-text>
        <v-list>
          <v-list-item
            v-for="(upload, index) in uploadHistory.slice(0, 10)"
            :key="index"
            class="history-item"
          >
            <template v-slot:prepend>
              <div class="history-icon" :style="`background: ${getFileColor(upload.file_name)}`">
                <v-icon color="white" size="24">{{ getFileIcon(upload.file_name) }}</v-icon>
              </div>
            </template>
            <v-list-item-title>{{ upload.file_name }}</v-list-item-title>
            <v-list-item-subtitle>
              {{ upload.document_type }} • {{ formatDate(upload.created_at) }}
            </v-list-item-subtitle>
            <template v-slot:append>
              <v-chip
                :color="getStatusColor(upload.status)"
                size="small"
              >
                <v-icon left size="16">{{ getStatusIcon(upload.status) }}</v-icon>
                {{ upload.status }}
              </v-chip>
            </template>
          </v-list-item>
        </v-list>
      </v-card-text>
    </v-card>
  </div>
</template>

<script>
import { format } from 'date-fns'
import * as XLSX from 'xlsx'

export default {
  name: 'UploadEnhanced',
  data() {
    return {
      documentType: 'RFP',
      processingMode: 'simple',
      selectedFiles: [],
      isDragging: false,
      uploading: false,
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
      documentCategories: [
        'Guidance',
        'White Paper',
        'User Manual',
        'Gap Document',
        'Technical Specification',
        'Best Practices'
      ],
      uploadHistory: [],
      stats: [
        { icon: 'mdi-upload', value: '0', label: 'Today\'s Uploads', color: 'primary' },
        { icon: 'mdi-file-check', value: '0', label: 'Total Processed', color: 'success' },
        { icon: 'mdi-clock-fast', value: '0', label: 'In Progress', color: 'warning' },
        { icon: 'mdi-harddisk', value: '0 MB', label: 'Storage Used', color: 'info' }
      ]
    }
  },
  computed: {
    acceptedFormats() {
      return this.documentType === 'RFP'
        ? '.xlsx,.xls,.xlsm'
        : '.pdf,.docx,.doc'
    },
    supportedFormats() {
      if (this.documentType === 'RFP') {
        return [
          { ext: 'XLSX', icon: 'mdi-microsoft-excel', color: 'success' },
          { ext: 'XLS', icon: 'mdi-microsoft-excel', color: 'success' },
          { ext: 'XLSM', icon: 'mdi-microsoft-excel', color: 'success' }
        ]
      } else {
        return [
          { ext: 'PDF', icon: 'mdi-file-pdf-box', color: 'error' },
          { ext: 'DOCX', icon: 'mdi-microsoft-word', color: 'info' },
          { ext: 'DOC', icon: 'mdi-microsoft-word', color: 'info' }
        ]
      }
    },
    isValid() {
      if (this.selectedFiles.length === 0) return false

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
    this.loadUploadHistory()
    this.loadStats()
  },
  methods: {
    handleDrop(e) {
      this.isDragging = false
      const files = Array.from(e.dataTransfer.files)
      this.processFiles(files)
    },
    handleFileSelect(e) {
      const files = Array.from(e.target.files)
      this.processFiles(files)
    },
    async processFiles(files) {
      for (const file of files) {
        if (!this.validateFile(file)) continue

        // Add file with progress tracking
        const fileObj = {
          name: file.name,
          size: file.size,
          file: file,
          progress: 0,
          speed: ''
        }

        // For Excel files, generate preview
        if (this.isExcelFile(file.name)) {
          try {
            const preview = await this.generateExcelPreview(file)
            fileObj.preview = preview
          } catch (error) {
            console.error('Preview error:', error)
          }
        }

        this.selectedFiles.push(fileObj)
      }

      this.$refs.fileInput.value = ''
    },
    validateFile(file) {
      // Size check
      const maxSize = 50 * 1024 * 1024
      if (file.size > maxSize) {
        this.showToast('error', `File "${file.name}" exceeds 50MB limit`)
        return false
      }

      // Type check
      const extension = this.getFileExtension(file.name)
      const validExtensions = this.documentType === 'RFP'
        ? ['xlsx', 'xls', 'xlsm']
        : ['pdf', 'docx', 'doc']

      if (!validExtensions.includes(extension)) {
        this.showToast('error', `Invalid file type "${extension}"`)
        return false
      }

      return true
    },
    async generateExcelPreview(file) {
      return new Promise((resolve, reject) => {
        const reader = new FileReader()
        reader.onload = (e) => {
          try {
            const data = new Uint8Array(e.target.result)
            const workbook = XLSX.read(data, { type: 'array' })
            const firstSheet = workbook.Sheets[workbook.SheetNames[0]]
            const jsonData = XLSX.utils.sheet_to_json(firstSheet, { header: 1 })

            if (jsonData.length > 0) {
              resolve({
                headers: jsonData[0] || [],
                rows: jsonData.slice(1, 4) || []
              })
            } else {
              resolve({ headers: [], rows: [] })
            }
          } catch (error) {
            reject(error)
          }
        }
        reader.onerror = reject
        reader.readAsArrayBuffer(file)
      })
    },
    removeFile(index) {
      this.selectedFiles.splice(index, 1)
    },
    clearAllFiles() {
      this.selectedFiles = []
      this.resetMetadata()
    },
    async uploadFiles() {
      if (!this.isValid) {
        this.showToast('warning', 'Please fill in all required fields')
        return
      }

      this.uploading = true

      try {
        const metadata = this.documentType === 'RFP'
          ? this.rfpMetadata
          : this.docMetadata

        // Upload files sequentially
        for (let i = 0; i < this.selectedFiles.length; i++) {
          const fileObj = this.selectedFiles[i]

          // Simulate progress
          const progressInterval = setInterval(() => {
            if (fileObj.progress < 90) {
              fileObj.progress += 10
              fileObj.speed = `${(Math.random() * 5 + 1).toFixed(1)} MB/s`
            }
          }, 200)

          try {
            const response = await this.$store.dispatch('uploadDocument', {
              file: fileObj.file,
              documentType: this.documentType,
              metadata,
              processingMode: this.processingMode
            })

            clearInterval(progressInterval)
            fileObj.progress = 100
            fileObj.speed = ''

            // Add to history
            this.uploadHistory.unshift({
              file_name: fileObj.name,
              document_type: this.documentType,
              status: 'Processing',
              created_at: new Date().toISOString(),
              ...response
            })

          } catch (error) {
            clearInterval(progressInterval)
            console.error('Upload error:', error)
            this.showToast('error', `Failed to upload ${fileObj.name}`)
          }
        }

        this.showToast('success', `Successfully uploaded ${this.selectedFiles.length} file(s)!`)

        // Save history
        localStorage.setItem('uploadHistory', JSON.stringify(this.uploadHistory))

        // Navigate based on mode
        if (this.documentType === 'RFP' && this.processingMode === 'professional') {
          setTimeout(() => {
            this.$router.push('/mapping')
          }, 1500)
        } else {
          setTimeout(() => {
            this.$router.push('/documents')
          }, 1500)
        }

      } catch (error) {
        console.error('Upload error:', error)
        this.showToast('error', 'Upload failed')
      } finally {
        this.uploading = false
        this.loadStats()
      }
    },
    resetMetadata() {
      this.rfpMetadata = { rfp_name: '', bank_name: '', product: '' }
      this.docMetadata = {
        document_name: '',
        related_product: '',
        submodule: '',
        document_category: '',
        tags: []
      }
    },
    loadUploadHistory() {
      const stored = localStorage.getItem('uploadHistory')
      if (stored) {
        this.uploadHistory = JSON.parse(stored)
      }
    },
    loadStats() {
      // Load stats from localStorage or API
      const history = this.uploadHistory
      const today = new Date().toDateString()
      const todayUploads = history.filter(u =>
        new Date(u.created_at).toDateString() === today
      ).length

      this.stats[0].value = todayUploads.toString()
      this.stats[1].value = history.length.toString()
      this.stats[2].value = history.filter(u => u.status === 'Processing').length.toString()
    },
    isExcelFile(filename) {
      const ext = this.getFileExtension(filename)
      return ['xlsx', 'xls', 'xlsm'].includes(ext)
    },
    getFileExtension(filename) {
      return filename.split('.').pop().toLowerCase()
    },
    getFileIcon(filename) {
      const ext = this.getFileExtension(filename)
      const iconMap = {
        xlsx: 'mdi-microsoft-excel',
        xls: 'mdi-microsoft-excel',
        xlsm: 'mdi-microsoft-excel',
        pdf: 'mdi-file-pdf-box',
        docx: 'mdi-microsoft-word',
        doc: 'mdi-microsoft-word'
      }
      return iconMap[ext] || 'mdi-file'
    },
    getFileColor(filename) {
      const ext = this.getFileExtension(filename)
      const colorMap = {
        xlsx: 'linear-gradient(135deg, #1e7e34, #28a745)',
        xls: 'linear-gradient(135deg, #1e7e34, #28a745)',
        xlsm: 'linear-gradient(135deg, #1e7e34, #28a745)',
        pdf: 'linear-gradient(135deg, #c82333, #dc3545)',
        docx: 'linear-gradient(135deg, #0056b3, #007bff)',
        doc: 'linear-gradient(135deg, #0056b3, #007bff)'
      }
      return colorMap[ext] || 'linear-gradient(135deg, #6c757d, #adb5bd)'
    },
    formatFileSize(bytes) {
      if (bytes === 0) return '0 Bytes'
      const k = 1024
      const sizes = ['Bytes', 'KB', 'MB', 'GB']
      const i = Math.floor(Math.log(bytes) / Math.log(k))
      return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
    },
    formatDate(dateString) {
      try {
        return format(new Date(dateString), 'MMM dd, yyyy HH:mm')
      } catch {
        return dateString
      }
    },
    getStatusColor(status) {
      const colors = {
        'Processing': 'warning',
        'Completed': 'success',
        'Failed': 'error',
        'Pending': 'info'
      }
      return colors[status] || 'default'
    },
    getStatusIcon(status) {
      const icons = {
        'Processing': 'mdi-progress-clock',
        'Completed': 'mdi-check-circle',
        'Failed': 'mdi-alert-circle',
        'Pending': 'mdi-clock-outline'
      }
      return icons[status] || 'mdi-help-circle'
    },
    showToast(type, message) {
      // Integrate with your toast/notification system
      console.log(`[${type}] ${message}`)
    }
  }
}
</script>

<style scoped>
.upload-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 24px;
}

/* Animated Header */
.upload-header {
  position: relative;
  overflow: hidden;
  border-radius: 16px;
  margin-bottom: 32px;
}

.header-gradient {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 48px 32px;
  position: relative;
}

.header-gradient::before {
  content: '';
  position: absolute;
  top: -50%;
  right: -50%;
  width: 200%;
  height: 200%;
  background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
  animation: shimmer 3s infinite;
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

.stat-icon-wrapper.info {
  background: linear-gradient(135deg, #4facfe, #00f2fe);
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

/* Selection Cards */
.selection-card {
  height: 100%;
  border-radius: 12px;
  transition: all 0.3s ease;
}

.selection-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 16px rgba(0,0,0,0.1);
}

/* Upload Zone */
.upload-zone-card {
  border-radius: 16px;
  border: 3px dashed #cbd5e0;
  cursor: pointer;
  transition: all 0.3s ease;
  background: linear-gradient(135deg, #f7fafc 0%, #edf2f7 100%);
}

.upload-zone-card.drag-active {
  border-color: #48bb78;
  background: linear-gradient(135deg, #f0fff4 0%, #c6f6d5 100%);
  transform: scale(1.02);
  box-shadow: 0 12px 32px rgba(72, 187, 120, 0.2);
}

.upload-zone-card.has-files {
  border-color: #667eea;
  background: linear-gradient(135deg, #faf5ff 0%, #e9d8fd 100%);
}

.upload-zone-content {
  padding: 64px 32px;
  text-align: center;
}

.upload-animation {
  position: relative;
  display: inline-block;
  margin-bottom: 24px;
}

.upload-icon {
  transition: all 0.3s ease;
  position: relative;
  z-index: 2;
}

.icon-circle {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 100px;
  height: 100px;
  border-radius: 50%;
  background: rgba(102, 126, 234, 0.1);
  animation: pulse 2s infinite;
}

.upload-title {
  font-size: 28px;
  font-weight: 700;
  margin-bottom: 8px;
  transition: color 0.3s ease;
}

.upload-subtitle {
  font-size: 16px;
  color: #718096;
}

.browse-text {
  color: #667eea;
  font-weight: 600;
  text-decoration: underline;
}

.format-chips {
  margin: 24px 0;
}

.upload-info {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  font-size: 14px;
  color: #a0aec0;
}

/* File Preview Cards */
.file-preview-card {
  border-radius: 12px;
  padding: 16px;
  transition: all 0.3s ease;
  animation: slideInRight 0.4s ease-out;
}

.file-preview-card:hover {
  box-shadow: 0 8px 24px rgba(0,0,0,0.12);
}

.file-preview-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.file-icon-large {
  width: 56px;
  height: 56px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.file-info {
  flex: 1;
  min-width: 0;
}

.file-name {
  font-size: 16px;
  font-weight: 600;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  margin-bottom: 4px;
}

.file-meta {
  display: flex;
  gap: 4px;
}

.file-progress {
  margin-top: 12px;
}

.progress-info {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
  font-size: 14px;
  font-weight: 600;
}

.upload-speed {
  color: #667eea;
}

.progress-status {
  margin-top: 8px;
  font-size: 13px;
  text-align: center;
}

/* Excel Preview */
.file-preview-data {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #e2e8f0;
}

.preview-label {
  font-size: 12px;
  font-weight: 600;
  color: #718096;
  margin-bottom: 8px;
  text-transform: uppercase;
}

.excel-preview {
  overflow-x: auto;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
}

.excel-row {
  display: flex;
  min-width: max-content;
}

.excel-header {
  background: #f7fafc;
  font-weight: 600;
  border-bottom: 2px solid #cbd5e0;
}

.excel-cell {
  padding: 8px 12px;
  font-size: 12px;
  border-right: 1px solid #e2e8f0;
  min-width: 120px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.excel-cell:last-child {
  border-right: none;
}

/* Metadata Card */
.metadata-card {
  border-radius: 12px;
  animation: slideInUp 0.5s ease-out;
}

/* Action Card */
.action-card {
  border-radius: 12px;
  box-shadow: 0 4px 16px rgba(0,0,0,0.1);
  animation: slideInUp 0.6s ease-out;
}

.upload-btn {
  padding: 0 32px !important;
  font-weight: 600;
}

/* History Card */
.history-card {
  border-radius: 12px;
  animation: fadeIn 0.8s ease-out;
}

.history-item {
  border-radius: 8px;
  margin-bottom: 8px;
  transition: background 0.2s ease;
}

.history-item:hover {
  background: #f7fafc;
}

.history-icon {
  width: 40px;
  height: 40px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
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

@keyframes slideInRight {
  from {
    opacity: 0;
    transform: translateX(20px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

@keyframes shimmer {
  0%, 100% {
    transform: rotate(0deg);
  }
  50% {
    transform: rotate(180deg);
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

@keyframes pulse {
  0%, 100% {
    transform: translate(-50%, -50%) scale(1);
    opacity: 0.3;
  }
  50% {
    transform: translate(-50%, -50%) scale(1.2);
    opacity: 0.1;
  }
}

/* Responsive */
@media (max-width: 960px) {
  .upload-container {
    padding: 16px;
  }

  .header-gradient {
    padding: 32px 16px;
  }

  .upload-zone-content {
    padding: 48px 24px;
  }

  .upload-title {
    font-size: 22px;
  }
}
</style>
