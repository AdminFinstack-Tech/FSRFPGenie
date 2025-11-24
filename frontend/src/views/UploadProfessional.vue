<template>
  <div class="upload-professional">
    <!-- Page Header -->
    <div class="page-header">
      <h1 class="page-title">Upload Document</h1>
      <p class="page-description">Upload RFP documents for processing and analysis</p>
    </div>

    <!-- Upload Area -->
    <div class="upload-section">
      <div 
        class="drop-zone"
        :class="{ 'drop-zone-active': isDragging }"
        @dragover.prevent="isDragging = true"
        @dragleave.prevent="isDragging = false"
        @drop.prevent="handleDrop"
        @click="triggerFileInput"
      >
        <input 
          ref="fileInput" 
          type="file" 
          accept=".pdf,.xlsx,.xls,.docx,.doc" 
          multiple 
          @change="handleFileSelect"
          style="display: none"
        />
        
        <v-icon size="64" color="#cbd5e1">mdi-cloud-upload-outline</v-icon>
        <div class="drop-zone-title">Drop files here or click to browse</div>
        <div class="drop-zone-subtitle">Supports PDF, Excel (.xlsx, .xls), and Word (.docx, .doc)</div>
      </div>

      <!-- Selected Files -->
      <div v-if="selectedFiles.length > 0" class="files-section">
        <div class="section-header">
          <h3 class="section-title">Selected Files ({{ selectedFiles.length }})</h3>
          <button class="btn-clear" @click="clearFiles">Clear All</button>
        </div>

        <div class="files-list">
          <div v-for="(file, index) in selectedFiles" :key="index" class="file-item">
            <div class="file-icon">
              <v-icon :color="getFileIconColor(file.name)">{{ getFileIcon(file.name) }}</v-icon>
            </div>
            <div class="file-details">
              <div class="file-name">{{ file.name }}</div>
              <div class="file-size">{{ formatFileSize(file.size) }}</div>
            </div>
            <button class="btn-remove" @click="removeFile(index)">
              <v-icon size="20" color="#64748b">mdi-close</v-icon>
            </button>
          </div>
        </div>

        <!-- Metadata Form -->
        <div class="metadata-form">
          <div class="metadata-header">
            <h3 class="section-title">Document Metadata</h3>
            <div class="metadata-badge">
              <v-icon size="14" color="#14b8a6">mdi-brain</v-icon>
              <span>AI-Powered Extraction</span>
            </div>
          </div>
          <p class="metadata-description">
            Metadata will be automatically extracted from filename using AI. You can override by filling these fields.
          </p>
          <div class="form-grid">
            <div class="form-field">
              <label class="form-label">Bank Name <span class="label-optional">(optional)</span></label>
              <input 
                v-model="metadata.bank_name" 
                type="text" 
                class="form-input"
                placeholder="Auto-extracted from filename"
              />
            </div>
            <div class="form-field">
              <label class="form-label">Product <span class="label-optional">(optional)</span></label>
              <input 
                v-model="metadata.product" 
                type="text" 
                class="form-input"
                placeholder="Auto-extracted from filename"
              />
            </div>
            <div class="form-field">
              <label class="form-label">RFP Name <span class="label-optional">(optional)</span></label>
              <input 
                v-model="metadata.rfp_name" 
                type="text" 
                class="form-input"
                placeholder="Auto-extracted from filename"
              />
            </div>
          </div>
        </div>

        <!-- Upload Button -->
        <div class="upload-actions">
          <button 
            class="btn-upload" 
            :disabled="uploading"
            @click="uploadFiles"
          >
            <v-icon v-if="!uploading" left color="white">mdi-cloud-upload</v-icon>
            <v-progress-circular 
              v-else 
              indeterminate 
              size="20" 
              width="2"
              color="white"
              class="btn-spinner"
            ></v-progress-circular>
            {{ uploading ? 'Uploading...' : 'Upload Files' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Upload Progress -->
    <div v-if="uploadResults.length > 0" class="results-section">
      <h3 class="section-title">Upload Results</h3>
      <div class="results-list">
        <div v-for="(result, index) in uploadResults" :key="index" class="result-item">
          <div class="result-icon">
            <v-icon :color="result.success ? '#22c55e' : '#ef4444'">
              {{ result.success ? 'mdi-check-circle' : 'mdi-alert-circle' }}
            </v-icon>
          </div>
          <div class="result-details">
            <div class="result-name">{{ result.fileName }}</div>
            <div class="result-message" :class="result.success ? 'text-success' : 'text-error'">
              {{ result.message }}
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
  name: 'UploadProfessional',
  data() {
    return {
      isDragging: false,
      selectedFiles: [],
      uploading: false,
      uploadResults: [],
      metadata: {
        bank_name: '',
        product: '',
        rfp_name: ''
      }
    }
  },
  methods: {
    triggerFileInput() {
      this.$refs.fileInput.click()
    },
    handleFileSelect(event) {
      const files = Array.from(event.target.files)
      this.addFiles(files)
    },
    handleDrop(event) {
      this.isDragging = false
      const files = Array.from(event.dataTransfer.files)
      this.addFiles(files)
    },
    addFiles(files) {
      const validExtensions = ['.pdf', '.xlsx', '.xls', '.docx', '.doc']
      const validFiles = files.filter(file => {
        const ext = '.' + file.name.split('.').pop().toLowerCase()
        return validExtensions.includes(ext)
      })
      this.selectedFiles.push(...validFiles)
    },
    removeFile(index) {
      this.selectedFiles.splice(index, 1)
    },
    clearFiles() {
      this.selectedFiles = []
      this.uploadResults = []
    },
    async uploadFiles() {
      if (this.selectedFiles.length === 0) return

      this.uploading = true
      this.uploadResults = []

      const API_URL = process.env.VUE_APP_API_URL || 'http://localhost:5000/api'

      for (const file of this.selectedFiles) {
        const formData = new FormData()
        formData.append('file', file)
        formData.append('document_type', 'RFP') // Required: RFP or Documentation
        formData.append('processing_mode', 'simple') // Auto-process without column mapping
        
        // Send metadata as JSON object if any fields are filled
        const metadata = {}
        if (this.metadata.bank_name) metadata.bank_name = this.metadata.bank_name
        if (this.metadata.product) metadata.product = this.metadata.product
        if (this.metadata.rfp_name) metadata.rfp_name = this.metadata.rfp_name
        
        if (Object.keys(metadata).length > 0) {
          formData.append('metadata', JSON.stringify(metadata))
        }

        try {
          const response = await axios.post(`${API_URL}/documents/upload`, formData, {
            headers: { 'Content-Type': 'multipart/form-data' }
          })
          
          this.uploadResults.push({
            fileName: file.name,
            success: true,
            message: response.data.message || 'Uploaded successfully'
          })
        } catch (error) {
          this.uploadResults.push({
            fileName: file.name,
            success: false,
            message: error.response?.data?.error || 'Upload failed'
          })
        }
      }

      this.uploading = false
      this.selectedFiles = []
      this.metadata = { bank_name: '', product: '', rfp_name: '' }
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
    formatFileSize(bytes) {
      if (bytes < 1024) return bytes + ' B'
      if (bytes < 1048576) return (bytes / 1024).toFixed(1) + ' KB'
      return (bytes / 1048576).toFixed(1) + ' MB'
    }
  }
}
</script>

<style scoped>
/* === Color System === */
.upload-professional {
  --slate-50:  #f8fafc;
  --slate-100: #f1f5f9;
  --slate-200: #e2e8f0;
  --slate-300: #cbd5e1;
  --slate-500: #64748b;
  --slate-600: #475569;
  --slate-900: #0f172a;
  --teal-500: #14b8a6;
  --teal-600: #0d9488;
}

.upload-professional {
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
}

.page-description {
  font-size: 16px;
  color: var(--slate-600);
  margin: 0;
}

/* === Drop Zone === */
.drop-zone {
  background-color: white;
  border: 2px dashed var(--slate-200);
  border-radius: 12px;
  padding: 64px 32px;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s ease;
}

.drop-zone:hover {
  border-color: var(--teal-500);
  background-color: var(--slate-50);
}

.drop-zone-active {
  border-color: var(--teal-500);
  background-color: var(--slate-50);
}

.drop-zone-title {
  font-size: 18px;
  font-weight: 600;
  color: var(--slate-900);
  margin: 16px 0 8px 0;
}

.drop-zone-subtitle {
  font-size: 14px;
  color: var(--slate-500);
}

/* === Files Section === */
.files-section {
  margin-top: 32px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.section-title {
  font-size: 18px;
  font-weight: 600;
  color: var(--slate-900);
  margin: 0;
}

.btn-clear {
  background-color: white;
  border: 1px solid var(--slate-300);
  border-radius: 6px;
  padding: 8px 16px;
  font-size: 14px;
  font-weight: 500;
  color: var(--slate-700);
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-clear:hover {
  background-color: var(--slate-50);
  border-color: var(--slate-400);
}

/* === Files List === */
.files-list {
  background-color: white;
  border: 1px solid var(--slate-200);
  border-radius: 8px;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.file-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background-color: var(--slate-50);
  border-radius: 6px;
}

.file-icon {
  width: 40px;
  height: 40px;
  background-color: white;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.file-details {
  flex: 1;
  min-width: 0;
}

.file-name {
  font-size: 14px;
  font-weight: 500;
  color: var(--slate-900);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.file-size {
  font-size: 12px;
  color: var(--slate-500);
  margin-top: 2px;
}

.btn-remove {
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
  flex-shrink: 0;
}

.btn-remove:hover {
  background-color: #fef2f2;
  border-color: #ef4444;
}

/* === Metadata Form === */
.metadata-form {
  margin-top: 24px;
  background-color: white;
  border: 1px solid var(--slate-200);
  border-radius: 8px;
  padding: 24px;
}

.metadata-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.metadata-badge {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 4px 12px;
  background-color: var(--teal-50);
  border: 1px solid #a7f3d0;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
  color: var(--teal-600);
}

.metadata-description {
  font-size: 13px;
  color: var(--slate-600);
  margin: 0 0 16px 0;
  line-height: 1.5;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 16px;
  margin-top: 16px;
}

.form-field {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-label {
  font-size: 14px;
  font-weight: 500;
  color: var(--slate-700);
}

.label-optional {
  font-size: 12px;
  font-weight: 400;
  color: var(--slate-500);
  font-style: italic;
}

.form-input {
  width: 100%;
  padding: 10px 12px;
  font-size: 14px;
  color: var(--slate-900);
  background-color: white;
  border: 1px solid var(--slate-300);
  border-radius: 6px;
  transition: all 0.2s ease;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}

.form-input:focus {
  outline: none;
  border-color: var(--teal-500);
  box-shadow: 0 0 0 3px rgba(20, 184, 166, 0.1);
}

.form-input::placeholder {
  color: var(--slate-400);
}

/* === Upload Actions === */
.upload-actions {
  margin-top: 24px;
  display: flex;
  justify-content: flex-end;
}

.btn-upload {
  background-color: var(--teal-500);
  color: white;
  border: none;
  border-radius: 8px;
  padding: 12px 32px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  gap: 8px;
}

.btn-upload:hover:not(:disabled) {
  background-color: var(--teal-600);
}

.btn-upload:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-spinner {
  margin-right: 8px;
}

/* === Results Section === */
.results-section {
  margin-top: 32px;
}

.results-list {
  background-color: white;
  border: 1px solid var(--slate-200);
  border-radius: 8px;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.result-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background-color: var(--slate-50);
  border-radius: 6px;
}

.result-icon {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.result-details {
  flex: 1;
}

.result-name {
  font-size: 14px;
  font-weight: 500;
  color: var(--slate-900);
}

.result-message {
  font-size: 12px;
  margin-top: 2px;
}

.text-success {
  color: #15803d;
}

.text-error {
  color: #991b1b;
}

/* === Responsive === */
@media (max-width: 768px) {
  .form-grid {
    grid-template-columns: 1fr;
  }
}
</style>
