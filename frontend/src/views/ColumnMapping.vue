<template>
  <div class="column-mapping-page">
    <!-- Modern Page Header with Gradient -->
    <div class="page-header mb-8">
      <div class="header-content">
        <div class="header-icon-wrapper">
          <v-icon size="40" color="white">mdi-table-arrow-right</v-icon>
        </div>
        <div>
          <h1 class="text-4xl font-bold text-white mb-2">Column Mapping Studio</h1>
          <p class="text-white/80 text-lg">Map your Excel columns to standardized RFP fields with intelligent suggestions</p>
        </div>
      </div>
      
      <!-- Progress Steps -->
      <div class="mapping-steps mt-6">
        <div class="step completed">
          <div class="step-number">
            <v-icon color="white" size="20">mdi-check</v-icon>
          </div>
          <span class="step-label">Upload File</span>
        </div>
        <div class="step-line completed"></div>
        <div class="step active">
          <div class="step-number">2</div>
          <span class="step-label">Map Columns</span>
        </div>
        <div class="step-line"></div>
        <div class="step">
          <div class="step-number">3</div>
          <span class="step-label">Process & Index</span>
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <v-card v-if="loading" class="loading-card pa-12 text-center elevation-3">
      <div class="loading-animation">
        <v-progress-circular indeterminate color="primary" size="64" width="6"></v-progress-circular>
      </div>
      <h3 class="text-h5 mt-6 font-weight-bold">Analyzing Excel Structure...</h3>
      <p class="text-body-1 text-gray-600 mt-2">Please wait while we process your file</p>
    </v-card>

    <!-- Mapping Interface -->
    <template v-else>
      <!-- File Info Card with Stats -->
      <v-card class="file-info-card mb-6 elevation-3">
        <div class="file-info-header">
          <div class="d-flex align-center">
            <div class="excel-icon-wrapper">
              <v-icon size="48" color="white">mdi-microsoft-excel</v-icon>
            </div>
            <div class="ml-4">
              <h3 class="text-h5 font-weight-bold mb-1">{{ documentInfo.file_name }}</h3>
              <div class="d-flex align-center gap-4 mt-2">
                <div class="stat-chip">
                  <v-icon size="16" class="mr-1">mdi-table-row</v-icon>
                  <span>{{ documentInfo.total_rows?.toLocaleString() }} rows</span>
                </div>
                <div class="stat-chip">
                  <v-icon size="16" class="mr-1">mdi-table-column</v-icon>
                  <span>{{ documentInfo.columns?.length }} columns</span>
                </div>
                <div class="stat-chip success">
                  <v-icon size="16" class="mr-1">mdi-check-circle</v-icon>
                  <span>Ready to map</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </v-card>

      <!-- Template Selection with Enhanced Design -->
      <v-card class="template-card mb-6 elevation-2" v-if="templates.length > 0">
        <div class="template-header">
          <v-icon color="primary" class="mr-3">mdi-file-document-outline</v-icon>
          <h3 class="text-h6 font-weight-bold">Quick Start with Templates</h3>
        </div>
        <v-divider></v-divider>
        <div class="pa-6">
          <v-select
            v-model="selectedTemplate"
            label="Select a pre-configured mapping template"
            :items="templates"
            item-text="template_name"
            item-value="template_id"
            variant="outlined"
            density="comfortable"
            clearable
            prepend-inner-icon="mdi-database-search"
            @change="applyTemplate"
          >
            <template v-slot:item="{ item, props }">
              <v-list-item v-bind="props" class="template-item">
                <template v-slot:prepend>
                  <v-avatar color="primary" size="32">
                    <v-icon color="white" size="18">mdi-file-star</v-icon>
                  </v-avatar>
                </template>
                <v-list-item-title class="font-weight-medium">{{ item.template_name }}</v-list-item-title>
                <v-list-item-subtitle>
                  Created {{ formatDate(item.created_at) }}
                </v-list-item-subtitle>
              </v-list-item>
            </template>
          </v-select>
          <p class="text-caption text-gray-600 mt-2">
            <v-icon size="14" class="mr-1">mdi-information</v-icon>
            Templates save time by automatically mapping columns based on previous configurations
          </p>
        </div>
      </v-card>

      <!-- Enhanced Column Mapping Section -->
      <v-card class="mapping-card mb-6 elevation-3">
        <div class="mapping-header">
          <div>
            <h3 class="text-h6 font-weight-bold">Column Mappings</h3>
            <p class="text-body-2 text-gray-600 mt-1">
              Match your Excel columns with our standardized RFP fields
            </p>
          </div>
          <div class="d-flex align-center gap-3">
            <v-chip color="primary" variant="outlined" class="mapping-count">
              {{ Object.keys(mappings).filter(k => mappings[k]).length }} / {{ requiredFields.length }} Mapped
            </v-chip>
            
            <!-- Auto/Manual Toggle -->
            <v-btn-toggle
              v-model="mappingMode"
              mandatory
              rounded="lg"
              density="compact"
              class="mode-toggle"
              @update:modelValue="onMappingModeChange"
            >
              <v-btn value="auto" size="small">
                <v-icon start size="18">mdi-auto-fix</v-icon>
                Auto
              </v-btn>
              <v-btn value="manual" size="small">
                <v-icon start size="18">mdi-hand-pointing-right</v-icon>
                Manual
              </v-btn>
            </v-btn-toggle>
          </div>
        </div>
        
        <!-- Auto Mode Info Banner -->
        <v-alert
          v-if="mappingMode === 'auto'"
          :type="isValid ? 'info' : 'warning'"
          variant="tonal"
          density="compact"
          class="ma-4"
        >
          <template v-slot:prepend>
            <v-icon>{{ isValid ? 'mdi-lightbulb-on' : 'mdi-alert' }}</v-icon>
          </template>
          <div class="d-flex align-center justify-space-between">
            <div>
              <strong v-if="isValid">Smart Auto-Mapping Active</strong>
              <strong v-else>Auto-Mapping Incomplete</strong>
              <span class="ml-2" v-if="isValid">
                We've automatically matched columns based on content analysis
              </span>
              <span class="ml-2" v-else>
                Some required fields couldn't be auto-mapped. Switch to Manual mode to complete.
              </span>
            </div>
            <v-btn
              size="small"
              variant="tonal"
              :color="isValid ? 'primary' : 'warning'"
              @click="reAutoSuggest"
            >
              <v-icon start size="16">mdi-refresh</v-icon>
              Re-analyze
            </v-btn>
          </div>
        </v-alert>
        
        <v-divider></v-divider>
        
        <!-- Column Headers -->
        <div class="mapping-columns-header">
          <div class="column-header source-header">
            <v-icon class="mr-2">mdi-table</v-icon>
            <span>Your Excel Columns</span>
          </div>
          <div class="column-header-spacer"></div>
          <div class="column-header target-header">
            <v-icon class="mr-2">mdi-target</v-icon>
            <span>Standard RFP Fields</span>
          </div>
        </div>

        <div class="mapping-container">
          <div
            v-for="(field, index) in requiredFields"
            :key="field.key"
            class="mapping-row-enhanced"
            :class="{ 'mapped': mappings[field.key], 'required': field.required }"
          >
            <div class="mapping-row-content">
              <!-- Source Column Selector -->
              <div class="source-column">
                <v-select
                  v-model="mappings[field.key]"
                  :label="`Select column for ${field.label}`"
                  :items="documentInfo.columns"
                  variant="outlined"
                  density="comfortable"
                  :rules="field.required ? [v => !!v || `${field.label} is required`] : []"
                  :hint="getColumnPreview(mappings[field.key])"
                  persistent-hint
                  clearable
                  :disabled="mappingMode === 'auto'"
                  prepend-inner-icon="mdi-table-column"
                >
                  <template v-slot:prepend v-if="mappingMode === 'auto' && mappings[field.key]">
                    <v-tooltip text="Auto-suggested based on content analysis" location="top">
                      <template v-slot:activator="{ props }">
                        <v-chip
                          v-bind="props"
                          size="x-small"
                          color="success"
                          variant="flat"
                          class="mr-2"
                        >
                          <v-icon start size="12">mdi-auto-fix</v-icon>
                          Auto
                        </v-chip>
                      </template>
                    </v-tooltip>
                  </template>
                  <template v-slot:item="{ item, props }">
                    <v-list-item v-bind="props" class="column-item">
                      <template v-slot:prepend>
                        <v-icon :color="mappings[field.key] === item.value ? 'primary' : 'grey'">
                          mdi-table-column
                        </v-icon>
                      </template>
                      <v-list-item-title class="font-weight-medium">{{ item.value }}</v-list-item-title>
                      <v-list-item-subtitle class="text-caption">
                        {{ getColumnPreview(item.value) }}
                      </v-list-item-subtitle>
                    </v-list-item>
                  </template>
                </v-select>
              </div>
              
              <!-- Mapping Arrow -->
              <div class="mapping-arrow">
                <div class="arrow-container" :class="{ 'active': mappings[field.key] }">
                  <v-icon :color="mappings[field.key] ? 'primary' : 'grey-lighten-1'" size="28">
                    mdi-arrow-right-bold
                  </v-icon>
                </div>
              </div>
              
              <!-- Target Field Display -->
              <div class="target-column">
                <div class="target-field-card" :class="{ 'has-mapping': mappings[field.key] }">
                  <div class="d-flex align-center justify-space-between mb-2">
                    <div class="field-title">
                      <v-icon size="20" :color="field.required ? 'error' : 'success'" class="mr-2">
                        {{ field.required ? 'mdi-asterisk' : 'mdi-check-circle-outline' }}
                      </v-icon>
                      <span class="font-weight-bold">{{ field.label }}</span>
                    </div>
                    <v-chip
                      v-if="field.required"
                      color="error"
                      size="x-small"
                      variant="tonal"
                    >
                      Required
                    </v-chip>
                  </div>
                  <p class="field-description">{{ field.description }}</p>
                  <div v-if="mappings[field.key]" class="mapped-preview mt-3">
                    <v-icon size="14" color="success" class="mr-1">mdi-check</v-icon>
                    <span class="text-caption">Mapped to: <strong>{{ mappings[field.key] }}</strong></span>
                  </div>
                </div>
              </div>
            </div>
            
            <!-- Row Divider -->
            <v-divider v-if="index < requiredFields.length - 1" class="my-4"></v-divider>
          </div>
        </div>

        <!-- Save Template Option -->
        <v-divider class="my-6"></v-divider>
        
        <div class="template-save-section pa-4">
          <v-checkbox
            v-model="saveAsTemplate"
            label="Save this mapping as a template for future use"
            color="primary"
            density="comfortable"
          >
            <template v-slot:label>
              <div class="d-flex align-center">
                <v-icon class="mr-2" color="primary">mdi-content-save</v-icon>
                <span class="font-weight-medium">Save this mapping as a template for future use</span>
              </div>
            </template>
          </v-checkbox>
          
          <v-expand-transition>
            <v-text-field
              v-if="saveAsTemplate"
              v-model="templateName"
              label="Template Name"
              placeholder="e.g., Standard Bank RFP Mapping"
              variant="outlined"
              density="comfortable"
              prepend-inner-icon="mdi-tag"
              :rules="[v => !saveAsTemplate || !!v || 'Template name is required']"
              class="mt-4"
            ></v-text-field>
          </v-expand-transition>
        </div>
      </v-card>

      <!-- Enhanced Data Preview -->
      <v-card class="preview-card mb-6 elevation-2">
        <div class="preview-header">
          <div>
            <h3 class="text-h6 font-weight-bold">Data Preview</h3>
            <p class="text-body-2 text-gray-600 mt-1">
              Preview of how your data will be mapped (showing first 5 rows)
            </p>
          </div>
          <v-chip color="success" variant="outlined">
            <v-icon start size="16">mdi-eye</v-icon>
            Live Preview
          </v-chip>
        </div>
        
        <v-divider></v-divider>
        
        <div class="preview-table-wrapper">
          <v-simple-table dense class="preview-table">
            <template v-slot:default>
              <thead>
                <tr>
                  <th v-for="field in requiredFields" :key="field.key" class="preview-th">
                    <div class="d-flex align-center">
                      <v-icon size="16" class="mr-2">mdi-table-column</v-icon>
                      {{ field.label }}
                    </div>
                  </th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(row, index) in previewData" :key="index" class="preview-row">
                  <td v-for="field in requiredFields" :key="field.key" class="preview-td">
                    <span class="preview-cell">
                      {{ row[mappings[field.key]] || '-' }}
                    </span>
                  </td>
                </tr>
                <tr v-if="!previewData || previewData.length === 0">
                  <td :colspan="requiredFields.length" class="text-center py-8">
                    <v-icon size="48" color="grey-lighten-1">mdi-table-off</v-icon>
                    <p class="text-body-2 text-gray-600 mt-2">No preview data available</p>
                  </td>
                </tr>
              </tbody>
            </template>
          </v-simple-table>
        </div>
      </v-card>

      <!-- Enhanced Action Buttons -->
      <div class="action-buttons">
        <v-btn
          size="large"
          variant="outlined"
          @click="$router.push('/upload')"
          class="action-btn"
          prepend-icon="mdi-arrow-left"
        >
          Back to Upload
        </v-btn>
        
        <v-btn
          size="large"
          color="primary"
          @click="submitMapping"
          :loading="submitting"
          :disabled="!isValid || submitting"
          class="action-btn process-btn"
          append-icon="mdi-rocket-launch"
        >
          <template v-if="!isValid">
            Complete Required Fields ({{ getMappedRequiredCount() }}/{{ getRequiredFieldsCount() }})
          </template>
          <template v-else>
            Process RFP Data
          </template>
        </v-btn>
      </div>
    </template>

    <!-- Processing Dialog -->
    <v-dialog v-model="processingDialog" persistent max-width="500">
      <v-card>
        <v-card-title class="text-h6">
          Processing RFP Data
        </v-card-title>
        <v-card-text class="py-6">
          <v-progress-linear
            :value="processingProgress"
            color="primary"
            height="8"
            rounded
            class="mb-4"
          ></v-progress-linear>
          <p class="text-center text-body-2">
            {{ processingStatus }}
          </p>
        </v-card-text>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
import { format } from 'date-fns'

export default {
  name: 'ColumnMapping',
  props: {
    documentId: {
      type: String,
      required: true
    }
  },
  data() {
    return {
      loading: true,
      submitting: false,
      documentInfo: {
        file_name: '',
        columns: [],
        total_rows: 0,
        preview_data: []
      },
      mappings: {
        product: '',
        requirement: '',
        requirement_category: '',
        response_category: '',
        effort_required: '',
        comments: ''
      },
      requiredFields: [
        {
          key: 'product',
          label: 'Product',
          description: 'Product or module name',
          required: true
        },
        {
          key: 'requirement',
          label: 'Requirement',
          description: 'Detailed requirement description',
          required: true
        },
        {
          key: 'requirement_category',
          label: 'Requirement Category',
          description: 'Priority level (Must Have, Critical, etc.)',
          required: true
        },
        {
          key: 'response_category',
          label: 'Response Category',
          description: 'Implementation approach',
          required: true
        },
        {
          key: 'effort_required',
          label: 'Effort Required',
          description: 'Implementation effort level',
          required: false
        },
        {
          key: 'comments',
          label: 'Comments',
          description: 'Additional notes or remarks',
          required: false
        }
      ],
      selectedTemplate: null,
      saveAsTemplate: false,
      templateName: '',
      processingDialog: false,
      processingProgress: 0,
      processingStatus: 'Initializing...',
      mappingMode: 'auto' // 'auto' or 'manual'
    }
  },
  computed: {
    templates() {
      return this.$store.state.templates
    },
    isValid() {
      // Check all required fields are mapped
      return this.requiredFields
        .filter(f => f.required)
        .every(f => this.mappings[f.key])
    },
    previewData() {
      return this.documentInfo.preview_data || []
    }
  },
  async mounted() {
    await this.loadTemplates()
    await this.loadDocumentInfo()
  },
  methods: {
    async loadTemplates() {
      try {
        await this.$store.dispatch('getTemplates')
      } catch (error) {
        console.error('Failed to load templates:', error)
      }
    },
    async loadDocumentInfo() {
      try {
        // Fetch real document information from backend
        const docInfo = await this.$store.dispatch('analyzeDocument', this.documentId)
        
        this.documentInfo = {
          file_name: docInfo.file_name,
          total_rows: docInfo.total_rows,
          columns: docInfo.columns,
          preview_data: docInfo.preview_data
        }
        
        console.log('Document info loaded:', this.documentInfo)
        
        // Auto-suggest mappings based on column names
        this.autoSuggestMappings()
        
      } catch (error) {
        console.error('Failed to load document:', error)
        this.$toast?.error('Failed to load document information')
      } finally {
        this.loading = false
      }
    },
    autoSuggestMappings() {
      // Enhanced intelligent mapping suggestions
      const mappingRules = {
        requirement: {
          keywords: ['requirement', 'feature', 'description', 'specification', 'spec', 'business', 'functional'],
          priority: 10,
          // Check if column has long text content (likely requirements)
          contentCheck: (colName, previewData) => {
            const avgLength = previewData.slice(0, 3).reduce((sum, row) => {
              const val = row[colName] || ''
              return sum + String(val).length
            }, 0) / Math.min(3, previewData.length)
            return avgLength > 50 // Long text = likely requirement
          }
        },
        product: {
          keywords: ['product', 'module', 'system', 'component', 'type', 'category'],
          priority: 8,
          contentCheck: (colName, previewData) => {
            // Short categorical text
            const avgLength = previewData.slice(0, 3).reduce((sum, row) => {
              const val = row[colName] || ''
              return sum + String(val).length
            }, 0) / Math.min(3, previewData.length)
            return avgLength > 5 && avgLength < 50
          }
        },
        requirement_category: {
          keywords: ['priority', 'category', 'level', 'type', 'class', 'team', 'responsible'],
          priority: 7
        },
        response_category: {
          keywords: ['response', 'status', 'availability', 'implementation', 'approach', 'vendor'],
          priority: 6
        },
        effort_required: {
          keywords: ['effort', 'complexity', 'work', 'hours', 'days', 'duration'],
          priority: 5
        },
        comments: {
          keywords: ['comment', 'note', 'remark', 'additional', 'description', 'detail'],
          priority: 4,
          contentCheck: (colName, previewData) => {
            // Very long text = likely comments
            const avgLength = previewData.slice(0, 3).reduce((sum, row) => {
              const val = row[colName] || ''
              return sum + String(val).length
            }, 0) / Math.min(3, previewData.length)
            return avgLength > 100
          }
        }
      }
      
      const scores = {}
      const previewData = this.documentInfo.preview_data || []
      
      // Calculate scores for each field-column combination
      this.requiredFields.forEach(field => {
        scores[field.key] = {}
        const rules = mappingRules[field.key] || { keywords: [], priority: 1 }
        
        this.documentInfo.columns.forEach(column => {
          let score = 0
          const columnLower = column.toLowerCase()
          
          // Check keyword matches
          rules.keywords?.forEach(keyword => {
            if (columnLower.includes(keyword.toLowerCase())) {
              score += 10
            }
          })
          
          // Apply content-based check if available
          if (rules.contentCheck && previewData.length > 0) {
            if (rules.contentCheck(column, previewData)) {
              score += 5
            }
          }
          
          // Apply priority weight
          score *= (rules.priority || 1)
          
          scores[field.key][column] = score
        })
      })
      
      // Assign best matches (avoiding duplicates)
      const usedColumns = new Set()
      
      // Sort fields by priority (required first, then by priority in rules)
      const sortedFields = [...this.requiredFields].sort((a, b) => {
        if (a.required && !b.required) return -1
        if (!a.required && b.required) return 1
        const aPriority = mappingRules[a.key]?.priority || 0
        const bPriority = mappingRules[b.key]?.priority || 0
        return bPriority - aPriority
      })
      
      sortedFields.forEach(field => {
        const fieldScores = scores[field.key]
        
        // Find best unused column
        let bestColumn = null
        let bestScore = 0
        
        Object.entries(fieldScores).forEach(([column, score]) => {
          if (!usedColumns.has(column) && score > bestScore) {
            bestScore = score
            bestColumn = column
          }
        })
        
        // For required fields, if no good match found, assign best available column
        if (field.required && !bestColumn && !usedColumns.has(bestColumn)) {
          // Find any unused column with some score
          const anyMatch = Object.entries(fieldScores)
            .filter(([col]) => !usedColumns.has(col))
            .sort((a, b) => b[1] - a[1])[0]
          
          if (anyMatch) {
            bestColumn = anyMatch[0]
            bestScore = anyMatch[1]
          }
        }
        
        // Assign mapping - lower threshold for required fields
        const threshold = field.required ? 0 : 3
        if (bestColumn && bestScore > threshold) {
          this.mappings[field.key] = bestColumn
          usedColumns.add(bestColumn)
        }
      })
      
      console.log('Auto-suggested mappings:', this.mappings)
      console.log('Mapping scores:', scores)
    },
    
    reAutoSuggest() {
      // Clear current mappings and re-run auto-suggest
      this.mappings = {
        product: '',
        requirement: '',
        requirement_category: '',
        response_category: '',
        effort_required: '',
        comments: ''
      }
      this.autoSuggestMappings()
      this.$toast?.success('Mappings re-analyzed successfully')
    },
    
    onMappingModeChange(mode) {
      if (mode === 'auto') {
        // Switch to auto mode - apply auto suggestions
        this.reAutoSuggest()
        this.$toast?.info('Auto-mapping enabled. Switch to Manual mode to customize.')
      } else {
        // Switch to manual mode
        this.$toast?.info('Manual mode enabled. You can now customize all mappings.')
      }
    },
    applyTemplate() {
      const template = this.templates.find(t => t.template_id === this.selectedTemplate)
      if (template) {
        this.mappings = { ...template.mappings }
        this.$toast.success('Template applied successfully')
      }
    },
    getColumnPreview(columnName) {
      if (!columnName || !this.previewData[0]) return ''
      const value = this.previewData[0][columnName]
      return value ? `"${value}"` : 'No data'
    },
    
    getMappedRequiredCount() {
      return this.requiredFields
        .filter(f => f.required)
        .filter(f => this.mappings[f.key])
        .length
    },
    
    getRequiredFieldsCount() {
      return this.requiredFields.filter(f => f.required).length
    },
    
    async submitMapping() {
      if (!this.isValid) {
        this.$toast?.warning('Please fill in all required fields')
        return
      }
      
      this.submitting = true
      this.processingDialog = true
      this.processingProgress = 0
      
      try {
        // Submit mapping
        this.processingStatus = 'Submitting column mappings...'
        this.processingProgress = 20
        
        const mappingResult = await this.$store.dispatch('submitColumnMapping', {
          documentId: this.documentId,
          mappings: this.mappings,
          saveTemplate: this.saveAsTemplate,
          templateName: this.templateName
        })
        
        console.log('Mapping submitted:', mappingResult)
        
        // Simulate processing progress
        this.processingStatus = 'Processing RFP records...'
        this.processingProgress = 50
        
        // Poll for status
        let attempts = 0
        const maxAttempts = 30
        
        while (attempts < maxAttempts) {
          await new Promise(resolve => setTimeout(resolve, 2000))
          
          try {
            const status = await this.$store.dispatch('getDocumentStatus', this.documentId)
            
            console.log('Document status:', status)
            
            if (status?.status === 'completed' || status?.status === 'failed' || status?.status === 'partial') {
              this.processingProgress = 100
              
              if (status.status === 'completed' || status.status === 'partial') {
                const recordCount = status.records_processed || 0
                this.processingStatus = `Successfully processed ${recordCount} records!`
                
                if (recordCount > 0) {
                  this.$toast?.success(`RFP data processed successfully! ${recordCount} records indexed.`)
                  
                  setTimeout(() => {
                    this.processingDialog = false
                    this.$router.push('/documents')
                  }, 2000)
                } else {
                  this.processingStatus = 'No records were processed. Please check your column mappings.'
                  this.$toast?.warning('Processing completed but no records were found.')
                  setTimeout(() => {
                    this.processingDialog = false
                  }, 3000)
                }
              } else {
                this.processingStatus = 'Processing failed'
                const errors = status.errors || status.error_details || []
                const errorMsg = errors.length > 0 ? errors[0].error : 'Unknown error'
                this.$toast?.error(`Failed to process RFP data: ${errorMsg}`)
                this.processingDialog = false
              }
              
              break
            }
            
            // Update progress
            if (status?.records_processed && status?.total_records) {
              const progressPercent = (status.records_processed / status.total_records) * 50
              this.processingProgress = 50 + progressPercent
              this.processingStatus = `Processing records: ${status.records_processed} / ${status.total_records}`
            }
            
            attempts++
          } catch (statusError) {
            console.warn('Status check error:', statusError)
            attempts++
          }
        }
        
        // Timeout handling
        if (attempts >= maxAttempts) {
          this.processingStatus = 'Processing timeout - please check document status later'
          this.$toast?.warning('Processing is taking longer than expected')
          setTimeout(() => {
            this.processingDialog = false
          }, 3000)
        }
        
      } catch (error) {
        console.error('Mapping submission error:', error)
        
        // Safe error message extraction
        let errorMessage = 'Failed to submit mapping'
        
        if (error?.response?.data?.error) {
          errorMessage = error.response.data.error
        } else if (error?.response?.data?.message) {
          errorMessage = error.response.data.message
        } else if (error?.message) {
          errorMessage = error.message
        }
        
        this.$toast?.error(errorMessage)
        this.processingDialog = false
      } finally {
        this.submitting = false
      }
    },
    formatDate(dateString) {
      return format(new Date(dateString), 'MMM d, yyyy')
    }
  }
}
</script>

<style scoped>
.column-mapping-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #e8edf2 100%);
  padding: 2rem;
}

/* ========== Page Header ========== */
.page-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 20px;
  padding: 2.5rem;
  box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
  margin-bottom: 2rem;
}

.header-content {
  display: flex;
  align-items: center;
  gap: 1.5rem;
}

.header-icon-wrapper {
  background: rgba(255, 255, 255, 0.2);
  border-radius: 16px;
  padding: 1.5rem;
  backdrop-filter: blur(10px);
}

/* Progress Steps */
.mapping-steps {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1rem;
}

.step {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
}

.step-number {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.2);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  transition: all 0.3s ease;
}

.step.completed .step-number,
.step.active .step-number {
  background: white;
  color: #667eea;
}

.step-label {
  color: rgba(255, 255, 255, 0.8);
  font-size: 0.85rem;
  font-weight: 500;
}

.step.completed .step-label,
.step.active .step-label {
  color: white;
}

.step-line {
  height: 2px;
  width: 60px;
  background: rgba(255, 255, 255, 0.3);
  transition: all 0.3s ease;
}

.step-line.completed {
  background: white;
}

/* ========== Cards ========== */
.loading-card,
.file-info-card,
.template-card,
.mapping-card,
.preview-card {
  border-radius: 16px;
  overflow: hidden;
  transition: all 0.3s ease;
}

.loading-card:hover,
.file-info-card:hover,
.template-card:hover,
.mapping-card:hover,
.preview-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.12);
}

/* ========== Loading Animation ========== */
.loading-animation {
  animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.05); }
}

/* ========== File Info Card ========== */
.file-info-header {
  padding: 2rem;
  background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%);
}

.excel-icon-wrapper {
  background: linear-gradient(135deg, #217346 0%, #185c37 100%);
  border-radius: 16px;
  padding: 1.5rem;
  box-shadow: 0 8px 20px rgba(33, 115, 70, 0.3);
}

.stat-chip {
  display: inline-flex;
  align-items: center;
  padding: 0.5rem 1rem;
  background: white;
  border-radius: 12px;
  font-size: 0.875rem;
  font-weight: 500;
  color: #4b5563;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  transition: all 0.2s ease;
}

.stat-chip:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.12);
}

.stat-chip.success {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  color: white;
}

/* ========== Template Card ========== */
.template-header {
  padding: 1.5rem;
  display: flex;
  align-items: center;
  background: #f9fafb;
}

.template-item {
  transition: background 0.2s ease;
}

.template-item:hover {
  background: #f3f4f6;
}

/* ========== Mapping Card ========== */
.mapping-header {
  padding: 1.5rem 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: linear-gradient(135deg, #667eea08 0%, #764ba208 100%);
}

.mapping-count {
  font-weight: 600;
}

/* Mode Toggle */
.mode-toggle {
  border: 2px solid #e5e7eb;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.mode-toggle .v-btn {
  text-transform: none;
  font-weight: 600;
  letter-spacing: 0;
}

.mode-toggle .v-btn--active {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
  color: white !important;
}

.mapping-columns-header {
  display: grid;
  grid-template-columns: 1fr 100px 1fr;
  gap: 1rem;
  padding: 1.5rem 2rem;
  background: #f9fafb;
  border-bottom: 2px solid #e5e7eb;
}

.column-header {
  display: flex;
  align-items: center;
  font-weight: 700;
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: #4b5563;
}

.mapping-container {
  padding: 2rem;
}

/* Enhanced Mapping Rows */
.mapping-row-enhanced {
  position: relative;
  transition: all 0.3s ease;
  padding: 1rem;
  border-radius: 12px;
}

.mapping-row-enhanced:hover {
  background: #f9fafb;
}

.mapping-row-enhanced.mapped {
  background: linear-gradient(135deg, #ecfdf510 0%, #d1fae510 100%);
  border-left: 4px solid #10b981;
}

.mapping-row-content {
  display: grid;
  grid-template-columns: 1fr 100px 1fr;
  gap: 1.5rem;
  align-items: start;
}

/* Source Column */
.source-column {
  position: relative;
}

/* Mapping Arrow */
.mapping-arrow {
  display: flex;
  align-items: center;
  justify-content: center;
  padding-top: 1rem;
}

.arrow-container {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background: #f3f4f6;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.arrow-container.active {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  transform: scale(1.1);
  box-shadow: 0 4px 16px rgba(102, 126, 234, 0.4);
}

.arrow-container.active .v-icon {
  animation: slideRight 0.6s ease-in-out;
}

@keyframes slideRight {
  0%, 100% { transform: translateX(0); }
  50% { transform: translateX(5px); }
}

/* Target Column */
.target-column {
  position: relative;
}

.target-field-card {
  padding: 1.25rem;
  background: #f9fafb;
  border: 2px dashed #d1d5db;
  border-radius: 12px;
  transition: all 0.3s ease;
  min-height: 100px;
}

.target-field-card.has-mapping {
  background: white;
  border: 2px solid #10b981;
  box-shadow: 0 4px 16px rgba(16, 185, 129, 0.1);
}

.field-title {
  display: flex;
  align-items: center;
  font-size: 1rem;
}

.field-description {
  color: #6b7280;
  font-size: 0.875rem;
  margin: 0.5rem 0 0 0;
  line-height: 1.5;
}

.mapped-preview {
  padding: 0.75rem;
  background: linear-gradient(135deg, #ecfdf5 0%, #d1fae5 100%);
  border-radius: 8px;
  display: flex;
  align-items: center;
}

/* Column Item in Dropdown */
.column-item {
  transition: background 0.2s ease;
  padding: 0.75rem 1rem;
}

.column-item:hover {
  background: #f3f4f6;
}

/* ========== Template Save Section ========== */
.template-save-section {
  background: linear-gradient(135deg, #fef3c715 0%, #fde68a15 100%);
  border-radius: 12px;
  margin: 1rem 0;
}

/* ========== Preview Card ========== */
.preview-header {
  padding: 1.5rem 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: linear-gradient(135deg, #667eea08 0%, #764ba208 100%);
}

.preview-table-wrapper {
  overflow-x: auto;
  max-height: 400px;
}

.preview-table {
  width: 100%;
}

.preview-th {
  background: #f9fafb !important;
  padding: 1rem !important;
  font-weight: 700 !important;
  color: #374151 !important;
  border-bottom: 2px solid #e5e7eb !important;
  white-space: nowrap;
}

.preview-row {
  transition: background 0.2s ease;
}

.preview-row:hover {
  background: #f9fafb;
}

.preview-td {
  padding: 1rem !important;
  border-bottom: 1px solid #e5e7eb !important;
}

.preview-cell {
  display: block;
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-size: 0.875rem;
  color: #1f2937;
}

/* ========== Action Buttons ========== */
.action-buttons {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  padding: 2rem 0;
}

.action-btn {
  padding: 1.5rem 2.5rem !important;
  font-weight: 600;
  text-transform: none;
  letter-spacing: 0.025em;
  border-radius: 12px;
  transition: all 0.3s ease;
}

.process-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
  box-shadow: 0 8px 20px rgba(102, 126, 234, 0.3);
}

.process-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 12px 28px rgba(102, 126, 234, 0.4);
}

/* ========== Responsive Design ========== */
@media (max-width: 960px) {
  .column-mapping-page {
    padding: 1rem;
  }
  
  .page-header {
    padding: 1.5rem;
  }
  
  .mapping-row-content {
    grid-template-columns: 1fr;
    gap: 1rem;
  }
  
  .mapping-columns-header {
    grid-template-columns: 1fr;
  }
  
  .column-header-spacer,
  .mapping-arrow {
    display: none;
  }
  
  .action-buttons {
    flex-direction: column-reverse;
  }
  
  .action-btn {
    width: 100%;
  }
}

/* ========== Animations ========== */
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.mapping-row-enhanced:nth-child(1) { animation: fadeIn 0.4s ease-out 0.05s backwards; }
.mapping-row-enhanced:nth-child(2) { animation: fadeIn 0.4s ease-out 0.1s backwards; }
.mapping-row-enhanced:nth-child(3) { animation: fadeIn 0.4s ease-out 0.15s backwards; }
.mapping-row-enhanced:nth-child(4) { animation: fadeIn 0.4s ease-out 0.2s backwards; }
.mapping-row-enhanced:nth-child(5) { animation: fadeIn 0.4s ease-out 0.25s backwards; }
.mapping-row-enhanced:nth-child(6) { animation: fadeIn 0.4s ease-out 0.3s backwards; }
</style>