<template>
  <div class="search-professional">
    <!-- Page Header -->
    <div class="page-header">
      <div class="header-left">
        <h1 class="page-title">Search RFPs</h1>
        <p class="page-description">Search through requirements and RFP responses</p>
      </div>
      <div class="header-actions">
        <v-btn 
          variant="outlined" 
          @click="toggleBookmarksView"
          prepend-icon="mdi-bookmark"
        >
          Bookmarks ({{ bookmarkedAnswers.length + bookmarkedResults.length }})
        </v-btn>
        
        <v-btn 
          v-if="searchHistory.length > 0"
          variant="outlined" 
          @click="showHistory = !showHistory"
          prepend-icon="mdi-history"
        >
          History
        </v-btn>
      </div>
    </div>

    <!-- Search Section -->
    <div class="search-section">
      <div class="search-input-container">
        <div class="search-input-wrapper">
          <v-icon size="24" color="#64748b">mdi-magnify</v-icon>
          <input 
            v-model="searchQuery" 
            type="text" 
            class="search-input-large"
            placeholder="Search requirements, responses, or keywords..."
            @keyup.enter="performSearch"
            @focus="showHistory = searchHistory.length > 0"
          />
          <button v-if="searchQuery" class="clear-btn" @click="clearSearch">
            <v-icon size="20" color="#64748b">mdi-close</v-icon>
          </button>
        </div>
        
        <!-- Search History Dropdown -->
        <div v-if="showHistory && searchHistory.length > 0" class="history-dropdown">
          <div class="history-header">
            <span>Recent Searches</span>
            <v-btn size="x-small" variant="text" @click="clearHistory">Clear</v-btn>
          </div>
          <div 
            v-for="(item, index) in searchHistory.slice(0, 10)" 
            :key="index"
            class="history-item"
            @click="selectHistoryItem(item.query)"
          >
            <v-icon size="16">mdi-history</v-icon>
            <span class="history-query">{{ item.query }}</span>
            <span class="history-count">{{ item.resultCount }} results</span>
          </div>
        </div>
      </div>
      
      <button class="btn-search" @click="performSearch" :disabled="!searchQuery || searching">
        <v-icon v-if="!searching" left color="white">mdi-magnify</v-icon>
        <v-progress-circular 
          v-else 
          indeterminate 
          size="20" 
          width="2"
          color="white"
          class="btn-spinner"
        ></v-progress-circular>
        {{ searching ? 'Searching...' : 'Search' }}
      </button>
    </div>

    <!-- Filters Section -->
    <div v-if="documents.length > 0 || results.length > 0" class="filters-section">
      <div class="filter-group">
        <label class="filter-label">Document</label>
        <select v-model="selectedDocument" class="filter-select" @change="performSearch">
          <option value="">All Documents</option>
          <option v-for="doc in documents" :key="doc.id" :value="doc.id">
            {{ doc.file_name }}
          </option>
        </select>
      </div>
      
      <div v-if="productOptions.length > 0" class="filter-group">
        <label class="filter-label">Product</label>
        <select v-model="filters.product" class="filter-select">
          <option value="">All Products</option>
          <option v-for="product in productOptions" :key="product" :value="product">
            {{ product }}
          </option>
        </select>
      </div>
      
      <div v-if="categoryOptions.length > 0" class="filter-group">
        <label class="filter-label">Category</label>
        <select v-model="filters.category" class="filter-select">
          <option value="">All Categories</option>
          <option v-for="category in categoryOptions" :key="category" :value="category">
            {{ category }}
          </option>
        </select>
      </div>
      
      <div v-if="bankOptions.length > 0" class="filter-group">
        <label class="filter-label">Bank</label>
        <select v-model="filters.bank" class="filter-select">
          <option value="">All Banks</option>
          <option v-for="bank in bankOptions" :key="bank" :value="bank">
            {{ bank }}
          </option>
        </select>
      </div>
    </div>

    <!-- Loading State with Skeleton -->
    <div v-if="searching" class="loading-state">
      <div class="skeleton-loader">
        <v-skeleton-loader 
          type="article, actions"
          v-for="i in 3" 
          :key="i"
          class="mb-4"
        ></v-skeleton-loader>
      </div>
    </div>

    <!-- Empty State (No Search Yet) -->
    <div v-else-if="!hasSearched && !searching" class="empty-state">
      <v-icon size="64" color="#cbd5e1">mdi-magnify</v-icon>
      <p class="empty-title">Start Your Search</p>
      <p class="empty-subtitle">Enter keywords to search through your RFP documents</p>
    </div>

    <!-- No Results -->
    <div v-else-if="hasSearched && results.length === 0 && !searching" class="empty-state">
      <v-icon size="64" color="#cbd5e1">mdi-file-search-outline</v-icon>
      <p class="empty-title">No Results Found</p>
      <p class="empty-subtitle">Try different keywords or check your filters</p>
    </div>

    <!-- Results -->
    <div v-else-if="results.length > 0" class="results-section">
      <!-- AI Answer Section -->
      <div v-if="aiAnswer" class="ai-answer-section">
        <div class="ai-answer-header">
          <v-icon size="24" color="#14b8a6">mdi-brain</v-icon>
          <h3 class="ai-answer-title">AI-Generated Answer</h3>
          <span class="confidence-badge" :class="confidenceClass">
            {{ Math.round(confidence * 100) }}% Confident
          </span>
          <v-chip size="small" color="#14b8a6" variant="outlined" class="mode-chip">
            {{ mode === 'intelligent' ? 'GPT-4o' : mode }}
          </v-chip>
          
          <!-- Action Buttons -->
          <div class="answer-actions">
            <v-tooltip text="Copy Answer" location="top">
              <template v-slot:activator="{ props }">
                <v-btn 
                  icon="mdi-content-copy" 
                  size="small" 
                  variant="tonal"
                  @click="copyAnswer"
                  v-bind="props"
                ></v-btn>
              </template>
            </v-tooltip>
            
            <v-tooltip text="Export Answer" location="top">
              <template v-slot:activator="{ props }">
                <v-btn 
                  icon="mdi-download" 
                  size="small" 
                  variant="tonal"
                  @click="exportAnswer"
                  v-bind="props"
                ></v-btn>
              </template>
            </v-tooltip>
            
            <v-tooltip :text="isAnswerBookmarked ? 'Remove Bookmark' : 'Bookmark Answer'" location="top">
              <template v-slot:activator="{ props }">
                <v-btn 
                  :icon="isAnswerBookmarked ? 'mdi-bookmark' : 'mdi-bookmark-outline'" 
                  size="small" 
                  variant="tonal"
                  :color="isAnswerBookmarked ? 'primary' : 'default'"
                  @click="bookmarkAnswer"
                  v-bind="props"
                ></v-btn>
              </template>
            </v-tooltip>
          </div>
        </div>
        <div class="ai-answer-content" v-html="formatAnswer(aiAnswer)"></div>
        
        <!-- Follow-up Questions -->
        <div v-if="suggestedQuestions.length > 0" class="follow-up-section">
          <div class="follow-up-header">
            <v-icon size="20" color="#f59e0b">mdi-lightbulb-on</v-icon>
            <h4>Suggested Questions:</h4>
          </div>
          <div class="question-chips">
            <v-chip 
              v-for="(question, index) in suggestedQuestions" 
              :key="index"
              @click="askFollowUp(question)"
              clickable
              prepend-icon="mdi-message-question"
              color="#14b8a6"
              variant="outlined"
              class="follow-up-chip"
            >
              {{ question }}
            </v-chip>
          </div>
        </div>
      </div>

      <div class="results-header">
        <h3 class="results-title">Source Documents ({{ filteredResults.length }})</h3>
        
        <div class="results-actions">
          <v-btn 
            variant="outlined" 
            size="small"
            @click="exportAllResults"
            prepend-icon="mdi-download"
          >
            Export All (CSV)
          </v-btn>
          
          <v-btn 
            v-if="selectedResults.length > 0"
            variant="outlined" 
            size="small"
            @click="exportSelected"
            prepend-icon="mdi-download"
            color="primary"
          >
            Export Selected ({{ selectedResults.length }})
          </v-btn>
        </div>
      </div>
      
      <!-- Selection Toolbar -->
      <div v-if="filteredResults.length > 0" class="selection-toolbar">
        <v-checkbox 
          v-model="selectAll"
          @change="toggleSelectAll"
          label="Select All"
          hide-details
          density="compact"
        ></v-checkbox>
        
        <span v-if="selectedResults.length > 0" class="selected-count">
          {{ selectedResults.length }} selected
        </span>
      </div>

      <div class="results-list">
        <transition-group name="fade-slide" tag="div">
          <div v-for="result in filteredResults" :key="result.record_id" class="result-card">
            <!-- Selection Checkbox -->
            <div class="result-selection">
              <v-checkbox 
                :model-value="selectedResults.includes(result.record_id)"
                @change="toggleResultSelection(result.record_id)"
                hide-details
                density="compact"
              ></v-checkbox>
            </div>
            
            <!-- Header with File Info and Score -->
            <div class="result-header">
              <div class="result-doc-info">
                <v-icon size="24" :color="getFileIconColor(result.file_name)" class="file-icon">
                  {{ getFileIcon(result.file_name) }}
                </v-icon>
              <div class="doc-details">
                <div class="doc-name">{{ result.file_name || 'Unknown Document' }}</div>
                <div class="doc-meta">
                  <span v-if="result.sheet_name" class="sheet-badge">
                    <v-icon size="12">mdi-table</v-icon>
                    {{ result.sheet_name }}
                  </span>
                  <span v-if="result.rfp_name && result.rfp_name !== 'Unknown RFP'" class="rfp-badge">
                    <v-icon size="12">mdi-file-document</v-icon>
                    {{ result.rfp_name }}
                  </span>
                </div>
              </div>
            </div>
            <div class="relevance-badge" v-if="result.relevance_score">
              <div class="score-circle">{{ Math.round(result.relevance_score * 100) }}%</div>
              <div class="score-label">Match</div>
            </div>
          </div>

          <!-- Content Section -->
          <div class="result-body">
            <!-- Requirement Text -->
            <div v-if="result.requirement" class="requirement-section">
              <div class="section-label">
                <v-icon size="16" color="#14b8a6">mdi-text-box-outline</v-icon>
                <span>Requirement</span>
              </div>
              <div class="section-content" v-html="result.highlight || highlightText(result.requirement)"></div>
            </div>
          </div>

          <!-- Footer with Tags and Actions -->
          <div class="result-footer">
            <div class="footer-tags">
              <span v-if="result.bank_name && result.bank_name !== 'Unknown Bank'" class="info-tag">
                <v-icon size="14">mdi-bank</v-icon>
                {{ result.bank_name }}
              </span>
              <span v-if="result.product" class="info-tag">
                <v-icon size="14">mdi-package-variant</v-icon>
                {{ result.product }}
              </span>
              <span v-if="result.requirement_category" class="info-tag category-tag">
                <v-icon size="14">mdi-tag</v-icon>
                {{ result.requirement_category }}
              </span>
            </div>
            
            <!-- Result Actions -->
            <div class="result-actions">
              <v-tooltip text="Copy Requirement" location="top">
                <template v-slot:activator="{ props }">
                  <v-btn 
                    icon="mdi-content-copy" 
                    size="x-small" 
                    variant="text"
                    @click="copyRequirement(result)"
                    v-bind="props"
                  ></v-btn>
                </template>
              </v-tooltip>
              
              <v-tooltip :text="isResultBookmarked(result) ? 'Remove Bookmark' : 'Bookmark'" location="top">
                <template v-slot:activator="{ props }">
                  <v-btn 
                    :icon="isResultBookmarked(result) ? 'mdi-bookmark' : 'mdi-bookmark-outline'" 
                    size="x-small" 
                    variant="text"
                    :color="isResultBookmarked(result) ? 'primary' : 'default'"
                    @click="bookmarkResult(result)"
                    v-bind="props"
                  ></v-btn>
                </template>
              </v-tooltip>
            </div>
          </div>
        </div>
        </transition-group>
      </div>
    </div>
    
    <!-- Sticky Summary (when scrolled) -->
    <div v-if="aiAnswer && scrolled" class="sticky-summary">
      <v-icon size="20">mdi-brain</v-icon>
      <span class="summary-text">{{ aiAnswerSummary }}</span>
      <v-btn size="small" variant="outlined" @click="scrollToAnswer">
        View Full Answer
      </v-btn>
    </div>
    
    <!-- Bookmarks View Modal -->
    <v-dialog v-model="showBookmarks" max-width="900px">
      <v-card>
        <v-card-title class="d-flex justify-space-between align-center">
          <span>Bookmarks</span>
          <v-btn icon="mdi-close" variant="text" @click="showBookmarks = false"></v-btn>
        </v-card-title>
        
        <v-card-text>
          <v-tabs v-model="bookmarkTab">
            <v-tab value="answers">Answers ({{ bookmarkedAnswers.length }})</v-tab>
            <v-tab value="results">Results ({{ bookmarkedResults.length }})</v-tab>
          </v-tabs>
          
          <v-window v-model="bookmarkTab" class="mt-4">
            <v-window-item value="answers">
              <div v-if="bookmarkedAnswers.length === 0" class="text-center py-8">
                <v-icon size="64" color="grey">mdi-bookmark-outline</v-icon>
                <p class="mt-4">No bookmarked answers yet</p>
              </div>
              <div v-else>
                <div v-for="(bookmark, index) in bookmarkedAnswers" :key="index" class="bookmark-item mb-4">
                  <div class="d-flex justify-space-between">
                    <strong>{{ bookmark.query }}</strong>
                    <v-btn icon="mdi-delete" size="x-small" variant="text" @click="bookmarkedAnswers.splice(index, 1); saveBookmarks()"></v-btn>
                  </div>
                  <p class="text-caption text-grey">
                    {{ new Date(bookmark.date).toLocaleString() }} • 
                    {{ bookmark.confidence ? Math.round(bookmark.confidence * 100) + '% confidence' : '' }} • 
                    {{ bookmark.sourceCount }} sources
                  </p>
                  <p class="mt-2">{{ bookmark.answer.substring(0, 200) }}...</p>
                </div>
              </div>
            </v-window-item>
            
            <v-window-item value="results">
              <div v-if="bookmarkedResults.length === 0" class="text-center py-8">
                <v-icon size="64" color="grey">mdi-bookmark-outline</v-icon>
                <p class="mt-4">No bookmarked results yet</p>
              </div>
              <div v-else>
                <div v-for="(result, index) in bookmarkedResults" :key="index" class="bookmark-item mb-4">
                  <div class="d-flex justify-space-between">
                    <strong>{{ result.file_name }}</strong>
                    <v-btn icon="mdi-delete" size="x-small" variant="text" @click="bookmarkedResults.splice(index, 1); saveBookmarks()"></v-btn>
                  </div>
                  <p class="text-caption text-grey">
                    {{ new Date(result.bookmarkedAt).toLocaleString() }}
                  </p>
                  <p class="mt-2">{{ result.requirement }}</p>
                </div>
              </div>
            </v-window-item>
          </v-window>
        </v-card-text>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'SearchProfessional',
  data() {
    return {
      searchQuery: '',
      searching: false,
      hasSearched: false,
      results: [],
      documents: [],
      selectedDocument: '',
      aiAnswer: '',
      confidence: 0,
      mode: 'intelligent',
      // Follow-up questions
      suggestedQuestions: [],
      // Bookmarks
      bookmarkedAnswers: [],
      bookmarkedResults: [],
      showBookmarks: false,
      bookmarkTab: 'answers',
      // Selection
      selectedResults: [],
      selectAll: false,
      // Advanced filters
      filters: {
        product: '',
        category: '',
        bank: ''
      },
      // Search history
      searchHistory: [],
      showHistory: false,
      // UI state
      scrolled: false,
      expandedResults: {}
    }
  },
  computed: {
    confidenceClass() {
      if (this.confidence >= 0.7) return 'confidence-high'
      if (this.confidence >= 0.5) return 'confidence-medium'
      return 'confidence-low'
    },
    productOptions() {
      return [...new Set(this.results.map(r => r.product).filter(Boolean))]
    },
    categoryOptions() {
      return [...new Set(this.results.map(r => r.requirement_category).filter(Boolean))]
    },
    bankOptions() {
      return [...new Set(this.results.map(r => r.bank_name).filter(Boolean))]
    },
    filteredResults() {
      let filtered = this.results
      
      if (this.filters.product) {
        filtered = filtered.filter(r => r.product === this.filters.product)
      }
      if (this.filters.category) {
        filtered = filtered.filter(r => r.requirement_category === this.filters.category)
      }
      if (this.filters.bank) {
        filtered = filtered.filter(r => r.bank_name === this.filters.bank)
      }
      
      return filtered
    },
    aiAnswerSummary() {
      if (!this.aiAnswer) return ''
      return this.aiAnswer.substring(0, 100) + '...'
    },
    isAnswerBookmarked() {
      return this.bookmarkedAnswers.some(b => b.query === this.searchQuery && b.answer === this.aiAnswer)
    }
  },
  mounted() {
    this.loadDocuments()
    this.loadBookmarks()
    this.loadSearchHistory()
    window.addEventListener('scroll', this.handleScroll)
  },
  beforeUnmount() {
    window.removeEventListener('scroll', this.handleScroll)
  },
  methods: {
    async loadDocuments() {
      try {
        const API_URL = process.env.VUE_APP_API_URL || 'http://localhost:5000/api'
        const response = await axios.get(`${API_URL}/documents`)
        this.documents = response.data.documents || []
      } catch (error) {
        console.error('Error loading documents:', error)
      }
    },
    async performSearch() {
      if (!this.searchQuery.trim()) return

      try {
        this.searching = true
        this.hasSearched = true
        
        const API_URL = process.env.VUE_APP_API_URL || 'http://localhost:5000/api'
        
        // Prepare filters
        const filters = {}
        if (this.selectedDocument) {
          filters.document_id = this.selectedDocument
        }

        // Use intelligent search with GPT-4o RAG
        const response = await axios.post(`${API_URL}/search/ask`, {
          question: this.searchQuery,
          filters: filters,
          max_context_docs: 50,
          temperature: 0.7,
          max_answer_length: 1000
        })
        
        // Store both AI answer and sources
        this.aiAnswer = response.data.answer || ''
        this.results = response.data.sources || []
        this.confidence = response.data.confidence || 0
        this.mode = response.data.mode || 'intelligent'
        
        // Generate follow-up questions
        if (this.aiAnswer) {
          this.generateFollowUpQuestions()
        }
        
        // Save to search history
        this.saveToSearchHistory()
        
      } catch (error) {
        console.error('Error searching:', error)
        this.results = []
        this.aiAnswer = ''
      } finally {
        this.searching = false
      }
    },
    clearSearch() {
      this.searchQuery = ''
      this.results = []
      this.hasSearched = false
      this.selectedDocument = ''
      this.aiAnswer = ''
      this.confidence = 0
    },
    formatAnswer(text) {
      if (!text) return ''
      
      // Convert markdown-style formatting to HTML
      let formatted = text
        .replace(/### (.*?)(\n|$)/g, '<h3>$1</h3>')
        .replace(/## (.*?)(\n|$)/g, '<h2>$1</h2>')
        .replace(/# (.*?)(\n|$)/g, '<h1>$1</h1>')
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.*?)\*/g, '<em>$1</em>')
        .replace(/\n\n/g, '</p><p>')
        .replace(/\n/g, '<br>')
      
      return `<p>${formatted}</p>`
    },
    highlightText(text) {
      if (!text || !this.searchQuery) return text
      
      const terms = this.searchQuery.split(' ').filter(t => t.length > 2)
      let highlighted = text
      
      terms.forEach(term => {
        const regex = new RegExp(`(${term})`, 'gi')
        highlighted = highlighted.replace(regex, '<mark>$1</mark>')
      })
      
      return highlighted
    },
    getFileIcon(filename) {
      if (!filename) return 'mdi-file-document'
      const ext = filename.split('.').pop().toLowerCase()
      if (ext === 'xlsx' || ext === 'xls') return 'mdi-file-excel'
      if (ext === 'pdf') return 'mdi-file-pdf-box'
      if (ext === 'docx' || ext === 'doc') return 'mdi-file-word'
      return 'mdi-file-document'
    },
    getFileIconColor(filename) {
      if (!filename) return '#64748b'
      const ext = filename.split('.').pop().toLowerCase()
      if (ext === 'xlsx' || ext === 'xls') return '#22c55e'
      if (ext === 'pdf') return '#ef4444'
      if (ext === 'docx' || ext === 'doc') return '#3b82f6'
      return '#64748b'
    },
    
    // === Follow-up Questions ===
    generateFollowUpQuestions() {
      const topics = this.extractTopics()
      this.suggestedQuestions = []
      
      if (topics.length > 0) {
        this.suggestedQuestions.push(`Can you provide more details about ${topics[0]}?`)
      }
      if (topics.length > 1) {
        this.suggestedQuestions.push(`What are the integration requirements for ${topics[1]}?`)
      }
      if (topics.length > 2) {
        this.suggestedQuestions.push(`Are there any compliance considerations for ${topics[2]}?`)
      }
      
      // Generic follow-ups
      this.suggestedQuestions.push(`What are the best practices for implementing this?`)
      this.suggestedQuestions.push(`Can you compare different approaches?`)
    },
    extractTopics() {
      if (!this.aiAnswer) return []
      
      // Extract key phrases from AI answer (simple implementation)
      const words = this.aiAnswer.toLowerCase().split(/\s+/)
      const commonWords = ['the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'is', 'are', 'was', 'were', 'be', 'been', 'being']
      const topics = words.filter(w => w.length > 5 && !commonWords.includes(w)).slice(0, 3)
      
      return topics
    },
    askFollowUp(question) {
      this.searchQuery = question
      this.performSearch()
      window.scrollTo({ top: 0, behavior: 'smooth' })
    },
    
    // === Copy to Clipboard ===
    async copyAnswer() {
      try {
        await navigator.clipboard.writeText(this.aiAnswer)
        this.showToast('Answer copied to clipboard!', 'success')
      } catch (error) {
        console.error('Copy failed:', error)
        this.showToast('Failed to copy', 'error')
      }
    },
    async copyRequirement(result) {
      try {
        const text = `${result.requirement}\n\nSource: ${result.file_name}`
        await navigator.clipboard.writeText(text)
        this.showToast('Requirement copied to clipboard!', 'success')
      } catch (error) {
        console.error('Copy failed:', error)
        this.showToast('Failed to copy', 'error')
      }
    },
    
    // === Export Functions ===
    exportAnswer() {
      if (!this.aiAnswer) return
      
      const content = `
SEARCH QUERY: ${this.searchQuery}
CONFIDENCE: ${Math.round(this.confidence * 100)}%
DATE: ${new Date().toLocaleString()}

AI ANSWER:
${this.aiAnswer}

SOURCE DOCUMENTS (${this.results.length}):
${this.results.map((r, i) => `
${i + 1}. ${r.file_name}
   Relevance: ${Math.round(r.relevance_score * 100)}%
   ${r.requirement}
`).join('\n')}
`
      
      this.downloadFile(content, `search-answer-${Date.now()}.txt`, 'text/plain')
      this.showToast('Answer exported!', 'success')
    },
    exportAllResults() {
      const csv = this.convertToCSV(this.filteredResults)
      this.downloadFile(csv, `search-results-${Date.now()}.csv`, 'text/csv')
      this.showToast(`Exported ${this.filteredResults.length} results!`, 'success')
    },
    exportSelected() {
      if (this.selectedResults.length === 0) {
        this.showToast('No results selected', 'warning')
        return
      }
      
      const selectedData = this.results.filter(r => this.selectedResults.includes(r.record_id))
      const csv = this.convertToCSV(selectedData)
      this.downloadFile(csv, `selected-results-${Date.now()}.csv`, 'text/csv')
      this.showToast(`Exported ${selectedData.length} selected results!`, 'success')
    },
    convertToCSV(data) {
      const headers = ['File Name', 'Sheet', 'RFP Name', 'Requirement', 'Category', 'Product', 'Bank', 'Relevance']
      const rows = data.map(r => [
        r.file_name || '',
        r.sheet_name || '',
        r.rfp_name || '',
        (r.requirement || '').replace(/"/g, '""'),
        r.requirement_category || '',
        r.product || '',
        r.bank_name || '',
        r.relevance_score ? Math.round(r.relevance_score * 100) + '%' : ''
      ])
      
      const csvContent = [
        headers.map(h => `"${h}"`).join(','),
        ...rows.map(row => row.map(cell => `"${cell}"`).join(','))
      ].join('\n')
      
      return csvContent
    },
    downloadFile(content, filename, type) {
      const blob = new Blob([content], { type })
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = filename
      a.click()
      window.URL.revokeObjectURL(url)
    },
    
    // === Bookmarks ===
    loadBookmarks() {
      const saved = localStorage.getItem('rfp_bookmarks')
      if (saved) {
        const data = JSON.parse(saved)
        this.bookmarkedAnswers = data.answers || []
        this.bookmarkedResults = data.results || []
      }
    },
    saveBookmarks() {
      localStorage.setItem('rfp_bookmarks', JSON.stringify({
        answers: this.bookmarkedAnswers,
        results: this.bookmarkedResults
      }))
    },
    bookmarkAnswer() {
      const bookmark = {
        query: this.searchQuery,
        answer: this.aiAnswer,
        confidence: this.confidence,
        date: new Date().toISOString(),
        sourceCount: this.results.length
      }
      
      const exists = this.bookmarkedAnswers.findIndex(b => b.query === this.searchQuery && b.answer === this.aiAnswer)
      
      if (exists >= 0) {
        this.bookmarkedAnswers.splice(exists, 1)
        this.showToast('Bookmark removed', 'info')
      } else {
        this.bookmarkedAnswers.unshift(bookmark)
        this.showToast('Answer bookmarked!', 'success')
      }
      
      this.saveBookmarks()
    },
    bookmarkResult(result) {
      const exists = this.bookmarkedResults.findIndex(b => b.record_id === result.record_id)
      
      if (exists >= 0) {
        this.bookmarkedResults.splice(exists, 1)
        this.showToast('Bookmark removed', 'info')
      } else {
        this.bookmarkedResults.unshift({ ...result, bookmarkedAt: new Date().toISOString() })
        this.showToast('Result bookmarked!', 'success')
      }
      
      this.saveBookmarks()
    },
    isResultBookmarked(result) {
      return this.bookmarkedResults.some(b => b.record_id === result.record_id)
    },
    toggleBookmarksView() {
      this.showBookmarks = !this.showBookmarks
    },
    
    // === Selection ===
    toggleSelectAll() {
      if (this.selectAll) {
        this.selectedResults = this.filteredResults.map(r => r.record_id)
      } else {
        this.selectedResults = []
      }
    },
    toggleResultSelection(recordId) {
      const index = this.selectedResults.indexOf(recordId)
      if (index >= 0) {
        this.selectedResults.splice(index, 1)
      } else {
        this.selectedResults.push(recordId)
      }
      
      this.selectAll = this.selectedResults.length === this.filteredResults.length
    },
    
    // === Search History ===
    loadSearchHistory() {
      const saved = localStorage.getItem('rfp_search_history')
      if (saved) {
        this.searchHistory = JSON.parse(saved)
      }
    },
    saveToSearchHistory() {
      const entry = {
        query: this.searchQuery,
        date: new Date().toISOString(),
        resultCount: this.results.length
      }
      
      // Remove duplicates
      this.searchHistory = this.searchHistory.filter(h => h.query !== this.searchQuery)
      this.searchHistory.unshift(entry)
      
      // Keep last 20
      this.searchHistory = this.searchHistory.slice(0, 20)
      
      localStorage.setItem('rfp_search_history', JSON.stringify(this.searchHistory))
    },
    selectHistoryItem(query) {
      this.searchQuery = query
      this.showHistory = false
      this.performSearch()
    },
    clearHistory() {
      this.searchHistory = []
      localStorage.removeItem('rfp_search_history')
      this.showToast('Search history cleared', 'info')
    },
    
    // === UI Helpers ===
    handleScroll() {
      this.scrolled = window.scrollY > 200
    },
    scrollToAnswer() {
      const element = document.querySelector('.ai-answer-section')
      if (element) {
        element.scrollIntoView({ behavior: 'smooth', block: 'start' })
      }
    },
    toggleResultExpand(recordId) {
      this.$set(this.expandedResults, recordId, !this.expandedResults[recordId])
    },
    showToast(message, type = 'info') {
      // Simple toast implementation (you can integrate with Vuetify snackbar)
      console.log(`[${type.toUpperCase()}] ${message}`)
      
      // Create a simple toast element
      const toast = document.createElement('div')
      toast.className = `toast toast-${type}`
      toast.textContent = message
      toast.style.cssText = `
        position: fixed;
        bottom: 24px;
        right: 24px;
        padding: 12px 24px;
        background: ${type === 'success' ? '#22c55e' : type === 'error' ? '#ef4444' : type === 'warning' ? '#f59e0b' : '#3b82f6'};
        color: white;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        z-index: 9999;
        animation: slideIn 0.3s ease;
      `
      
      document.body.appendChild(toast)
      
      setTimeout(() => {
        toast.style.animation = 'slideOut 0.3s ease'
        setTimeout(() => toast.remove(), 300)
      }, 3000)
    }
  }
}
</script>

<style scoped>
/* === Color System === */
.search-professional {
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
  --teal-50: #f0fdfa;
}

.search-professional {
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

/* === Search Section === */
.search-section {
  display: flex;
  gap: 12px;
  margin-bottom: 24px;
}

.search-input-wrapper {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 20px;
  background-color: white;
  border: 1px solid var(--slate-300);
  border-radius: 8px;
  transition: all 0.2s ease;
}

.search-input-wrapper:focus-within {
  border-color: var(--teal-500);
  box-shadow: 0 0 0 3px rgba(20, 184, 166, 0.1);
}

.search-input-large {
  flex: 1;
  border: none;
  outline: none;
  font-size: 16px;
  color: var(--slate-900);
  background: transparent;
}

.search-input-large::placeholder {
  color: var(--slate-400);
}

.clear-btn {
  background: transparent;
  border: none;
  cursor: pointer;
  padding: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.clear-btn:hover {
  background-color: var(--slate-100);
  border-radius: 4px;
}

.btn-search {
  background-color: var(--teal-500);
  color: white;
  border: none;
  border-radius: 8px;
  padding: 14px 32px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  gap: 8px;
  white-space: nowrap;
}

.btn-search:hover:not(:disabled) {
  background-color: var(--teal-600);
}

.btn-search:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-spinner {
  margin-right: 8px;
}

/* === Filters Section === */
.filters-section {
  display: flex;
  gap: 16px;
  margin-bottom: 24px;
  padding: 20px;
  background-color: white;
  border: 1px solid var(--slate-200);
  border-radius: 8px;
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
  min-width: 250px;
}

.filter-label {
  font-size: 14px;
  font-weight: 500;
  color: var(--slate-700);
}

.filter-select {
  padding: 10px 12px;
  font-size: 14px;
  color: var(--slate-900);
  background-color: white;
  border: 1px solid var(--slate-300);
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.filter-select:focus {
  outline: none;
  border-color: var(--teal-500);
  box-shadow: 0 0 0 3px rgba(20, 184, 166, 0.1);
}

/* === AI Answer Section === */
.ai-answer-section {
  background: linear-gradient(135deg, #f0fdfa 0%, #ffffff 100%);
  border: 2px solid #14b8a6;
  border-radius: 12px;
  padding: 24px;
  margin-bottom: 32px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}

.ai-answer-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
  padding-bottom: 16px;
  border-bottom: 1px solid #e2e8f0;
}

.ai-answer-title {
  font-size: 18px;
  font-weight: 600;
  color: #0f172a;
  margin: 0;
  flex: 1;
}

.confidence-badge {
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
}

.confidence-high {
  background-color: #d1fae5;
  color: #065f46;
}

.confidence-medium {
  background-color: #fef3c7;
  color: #92400e;
}

.confidence-low {
  background-color: #fee2e2;
  color: #991b1b;
}

.mode-chip {
  font-size: 11px;
  font-weight: 600;
}

.ai-answer-content {
  color: #334155;
  font-size: 15px;
  line-height: 1.7;
}

.ai-answer-content h1,
.ai-answer-content h2,
.ai-answer-content h3 {
  color: #0f172a;
  font-weight: 600;
  margin: 16px 0 8px 0;
}

.ai-answer-content h1 { font-size: 20px; }
.ai-answer-content h2 { font-size: 18px; }
.ai-answer-content h3 { font-size: 16px; }
.ai-answer-content strong {
  color: #14b8a6;
  font-weight: 600;
}
.ai-answer-content p { margin: 12px 0; }

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
  margin: 0;
}

/* === Results Section === */
.results-header {
  margin-bottom: 16px;
}

.results-title {
  font-size: 18px;
  font-weight: 600;
  color: var(--slate-900);
  margin: 0;
}

.results-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

/* === Result Card === */
.result-card {
  background-color: white;
  border: 1px solid var(--slate-200);
  border-radius: 12px;
  overflow: hidden;
  transition: all 0.2s ease;
}

.result-card:hover {
  border-color: var(--teal-500);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.result-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 20px 20px 16px 20px;
  background: linear-gradient(to bottom, #f8fafc, white);
  border-bottom: 1px solid var(--slate-100);
  gap: 16px;
}

.result-doc-info {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  flex: 1;
  min-width: 0;
}

.file-icon {
  flex-shrink: 0;
  margin-top: 2px;
}

.doc-details {
  flex: 1;
  min-width: 0;
}

.doc-name {
  font-size: 15px;
  font-weight: 600;
  color: var(--slate-900);
  margin-bottom: 6px;
  line-height: 1.4;
}

.doc-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.sheet-badge,
.rfp-badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 11px;
  color: var(--slate-600);
  background-color: var(--slate-100);
  padding: 3px 8px;
  border-radius: 4px;
  font-weight: 500;
}

.rfp-badge {
  background-color: var(--teal-50);
  color: var(--teal-700);
}

.relevance-badge {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  flex-shrink: 0;
}

.score-circle {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--teal-500), var(--teal-600));
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  font-weight: 700;
  box-shadow: 0 2px 8px rgba(20, 184, 166, 0.3);
}

.score-label {
  font-size: 11px;
  color: var(--slate-500);
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.result-body {
  padding: 20px;
}

.requirement-section {
  margin-bottom: 0;
}

.section-label {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  font-weight: 600;
  color: var(--slate-700);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 12px;
}

.section-content {
  font-size: 14px;
  color: var(--slate-700);
  line-height: 1.7;
  padding: 12px;
  background-color: var(--slate-50);
  border-radius: 6px;
  border-left: 3px solid var(--teal-500);
}

.section-content :deep(strong),
.section-content :deep(b) {
  color: var(--teal-700);
  font-weight: 600;
  background-color: var(--teal-50);
  padding: 2px 4px;
  border-radius: 3px;
}

.result-footer {
  padding: 12px 20px;
  background-color: var(--slate-50);
  border-top: 1px solid var(--slate-100);
}

.footer-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.info-tag {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  font-size: 12px;
  color: var(--slate-600);
  background-color: white;
  padding: 5px 12px;
  border-radius: 6px;
  border: 1px solid var(--slate-200);
  font-weight: 500;
}

.category-tag {
  background-color: var(--teal-50);
  color: var(--teal-700);
  border-color: var(--teal-200);
}

/* === NEW FEATURES === */

/* Header Actions */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.header-left {
  flex: 1;
}

.header-actions {
  display: flex;
  gap: 12px;
}

/* Search History Dropdown */
.search-input-container {
  flex: 1;
  position: relative;
}

.history-dropdown {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  margin-top: 8px;
  background: white;
  border: 1px solid var(--slate-200);
  border-radius: 8px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
  z-index: 100;
  max-height: 400px;
  overflow-y: auto;
}

.history-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  border-bottom: 1px solid var(--slate-200);
  font-weight: 600;
  font-size: 14px;
  color: var(--slate-700);
}

.history-item {
  padding: 12px 16px;
  display: flex;
  align-items: center;
  gap: 12px;
  cursor: pointer;
  transition: background-color 0.2s;
  border-bottom: 1px solid var(--slate-100);
}

.history-item:hover {
  background-color: var(--slate-50);
}

.history-item:last-child {
  border-bottom: none;
}

.history-query {
  flex: 1;
  font-size: 14px;
  color: var(--slate-700);
}

.history-count {
  font-size: 12px;
  color: var(--slate-500);
}

/* Answer Actions */
.answer-actions {
  display: flex;
  gap: 8px;
  margin-left: auto;
}

/* Follow-up Questions */
.follow-up-section {
  margin-top: 24px;
  padding: 20px;
  background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
  border-radius: 12px;
  border: 1px solid #fcd34d;
}

.follow-up-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 16px;
}

.follow-up-header h4 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: var(--slate-900);
}

.question-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.follow-up-chip {
  cursor: pointer;
  transition: transform 0.2s;
}

.follow-up-chip:hover {
  transform: translateY(-2px);
}

/* Results Header Actions */
.results-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.results-actions {
  display: flex;
  gap: 12px;
}

/* Selection Toolbar */
.selection-toolbar {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 12px 20px;
  background: var(--slate-50);
  border: 1px solid var(--slate-200);
  border-radius: 8px;
  margin-bottom: 16px;
}

.selected-count {
  font-size: 14px;
  font-weight: 600;
  color: var(--teal-600);
}

/* Result Card Enhancements */
.result-card {
  position: relative;
  display: flex;
  gap: 16px;
}

.result-selection {
  display: flex;
  align-items: flex-start;
  padding-top: 20px;
}

.result-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.result-actions {
  display: flex;
  gap: 4px;
}

/* Sticky Summary */
.sticky-summary {
  position: fixed;
  top: 80px;
  left: 50%;
  transform: translateX(-50%);
  background: white;
  padding: 16px 24px;
  border-radius: 12px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.15);
  display: flex;
  align-items: center;
  gap: 16px;
  max-width: 800px;
  z-index: 1000;
  animation: slideDown 0.3s ease;
}

.summary-text {
  flex: 1;
  font-size: 14px;
  color: var(--slate-700);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* Bookmarks Dialog */
.bookmark-item {
  padding: 16px;
  border: 1px solid var(--slate-200);
  border-radius: 8px;
  background: var(--slate-50);
}

.bookmark-item strong {
  color: var(--slate-900);
  font-size: 16px;
}

.bookmark-item p {
  margin: 4px 0 0 0;
  color: var(--slate-600);
}

/* Loading Skeleton */
.skeleton-loader {
  padding: 24px 0;
}

/* Animations */
@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateX(-50%) translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateX(-50%) translateY(0);
  }
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateX(100%);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

@keyframes slideOut {
  from {
    opacity: 1;
    transform: translateX(0);
  }
  to {
    opacity: 0;
    transform: translateX(100%);
  }
}

.fade-slide-enter-active,
.fade-slide-leave-active {
  transition: all 0.3s ease;
}

.fade-slide-enter-from {
  opacity: 0;
  transform: translateY(20px);
}

.fade-slide-leave-to {
  opacity: 0;
  transform: translateY(-20px);
}

/* === Responsive === */
@media (max-width: 768px) {
  .search-section {
    flex-direction: column;
  }
  
  .btn-search {
    width: 100%;
    justify-content: center;
  }
  
  .filters-section {
    flex-direction: column;
  }
  
  .filter-group {
    min-width: 0;
  }
  
  .result-header {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .result-meta {
    width: 100%;
    justify-content: flex-start;
  }
  
  .header-actions {
    margin-top: 16px;
  }
  
  .page-header {
    flex-direction: column;
  }
  
  .sticky-summary {
    max-width: 90%;
    padding: 12px 16px;
  }
  
  .results-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
  
  .results-actions {
    width: 100%;
    flex-direction: column;
  }
}
</style>
