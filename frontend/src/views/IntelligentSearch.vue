<template>
  <div>
    <!-- Page Header -->
    <div class="mb-8">
      <h1 class="text-3xl font-bold text-gray-900 mb-2">
        <v-icon class="mr-2" size="32" color="primary">mdi-robot</v-icon>
        Intelligent RFP Assistant
      </h1>
      <p class="text-gray-600">Ask questions in natural language and get AI-powered answers from your RFP documents</p>
    </div>

    <!-- Mode Toggle -->
    <v-card class="mb-6 pa-4">
      <div class="d-flex align-center justify-space-between">
        <div>
          <h3 class="text-h6 mb-1">Search Mode</h3>
          <p class="text-caption text-gray-600">Choose how you want to search</p>
        </div>
        <v-btn-toggle
          v-model="searchMode"
          mandatory
          rounded="lg"
          color="primary"
          class="mode-toggle"
        >
          <v-btn value="intelligent" class="px-6">
            <v-icon left>mdi-brain</v-icon>
            AI Answer
          </v-btn>
          <v-btn value="search" class="px-6">
            <v-icon left>mdi-magnify</v-icon>
            Vector Search
          </v-btn>
        </v-btn-toggle>
      </div>
    </v-card>

    <!-- Search/Question Input -->
    <v-card class="mb-6 pa-6">
      <v-textarea
        v-model="searchQuery"
        :placeholder="searchMode === 'intelligent' ? 
          'Ask a question: What are the fraud detection requirements?' : 
          'Search query: fraud detection features'"
        prepend-inner-icon="mdi-comment-question"
        variant="outlined"
        rows="2"
        auto-grow
        clearable
        @keyup.ctrl.enter="performSearch"
        @click:clear="clearSearch"
        hide-details
      >
        <template v-slot:append>
          <v-btn
            color="primary"
            size="large"
            @click="performSearch"
            :loading="loading"
            :disabled="!searchQuery"
            class="ml-2"
          >
            <v-icon left>{{ searchMode === 'intelligent' ? 'mdi-send' : 'mdi-magnify' }}</v-icon>
            {{ searchMode === 'intelligent' ? 'Ask' : 'Search' }}
          </v-btn>
        </template>
      </v-textarea>

      <!-- AI Settings (for intelligent mode) -->
      <v-expand-transition>
        <div v-if="searchMode === 'intelligent' && showAISettings" class="mt-4">
          <v-divider class="mb-4"></v-divider>
          <v-row>
            <v-col cols="12" md="4">
              <v-slider
                v-model="aiSettings.temperature"
                label="Creativity"
                :min="0"
                :max="1"
                :step="0.1"
                thumb-label
                hint="0 = Focused, 1 = Creative"
                persistent-hint
              >
                <template v-slot:prepend>
                  <v-icon>mdi-brain-freeze</v-icon>
                </template>
              </v-slider>
            </v-col>
            <v-col cols="12" md="4">
              <v-slider
                v-model="aiSettings.top_n"
                label="Context Documents"
                :min="3"
                :max="10"
                :step="1"
                thumb-label
                hint="Number of documents to analyze"
                persistent-hint
              >
                <template v-slot:prepend>
                  <v-icon>mdi-file-multiple</v-icon>
                </template>
              </v-slider>
            </v-col>
            <v-col cols="12" md="4">
              <v-slider
                v-model="aiSettings.max_tokens"
                label="Answer Length"
                :min="500"
                :max="2000"
                :step="100"
                thumb-label
                hint="Maximum answer length"
                persistent-hint
              >
                <template v-slot:prepend>
                  <v-icon>mdi-text-long</v-icon>
                </template>
              </v-slider>
            </v-col>
          </v-row>
        </div>
      </v-expand-transition>

      <!-- Filters -->
      <v-expand-transition>
        <div v-if="showFilters" class="mt-4">
          <v-divider class="mb-4"></v-divider>
          <v-row>
            <v-col cols="12" md="4">
              <v-select
                v-model="filters.products"
                label="Products"
                :items="availableProducts"
                multiple
                chips
                closable-chips
                clearable
                density="compact"
              ></v-select>
            </v-col>
            <v-col cols="12" md="4">
              <v-select
                v-model="filters.response_categories"
                label="Response Category"
                :items="responseCategories"
                multiple
                chips
                closable-chips
                clearable
                density="compact"
              ></v-select>
            </v-col>
            <v-col cols="12" md="4">
              <v-select
                v-model="filters.requirement_category"
                label="Requirement Category"
                :items="requirementCategories"
                multiple
                chips
                closable-chips
                clearable
                density="compact"
              ></v-select>
            </v-col>
          </v-row>
        </div>
      </v-expand-transition>

      <!-- Filter and AI Settings buttons hidden as per requirements -->
      <div v-if="false" class="mt-3 text-center d-flex gap-2 justify-center">
        <v-btn
          text
          small
          @click="showFilters = !showFilters"
        >
          <v-icon left small>{{ showFilters ? 'mdi-chevron-up' : 'mdi-chevron-down' }}</v-icon>
          {{ showFilters ? 'Hide' : 'Show' }} Filters
        </v-btn>
        <v-btn
          v-if="searchMode === 'intelligent'"
          text
          small
          @click="showAISettings = !showAISettings"
        >
          <v-icon left small>{{ showAISettings ? 'mdi-chevron-up' : 'mdi-chevron-down' }}</v-icon>
          {{ showAISettings ? 'Hide' : 'Show' }} AI Settings
        </v-btn>
      </div>
    </v-card>

    <!-- AI Answer (Intelligent Mode) -->
    <div v-if="hasSearched && searchMode === 'intelligent'">
      <!-- Answer Card -->
      <v-card class="mb-6" v-if="intelligentAnswer">
        <v-card-title class="d-flex align-center justify-space-between bg-gradient-primary text-white">
          <div class="d-flex align-center">
            <v-icon class="mr-2" color="white">mdi-robot-happy</v-icon>
            <span>AI Answer</span>
          </div>
          <div class="d-flex align-center gap-2">
            <v-chip
              :color="getModeColor(intelligentAnswer.mode)"
              size="small"
              dark
            >
              {{ intelligentAnswer.mode }}
            </v-chip>
            <v-chip
              v-if="intelligentAnswer.confidence"
              :color="getConfidenceColor(intelligentAnswer.confidence)"
              size="small"
              dark
            >
              {{ (intelligentAnswer.confidence * 100).toFixed(0) }}% confidence
            </v-chip>
          </div>
        </v-card-title>

        <v-card-text class="pa-6">
          <div class="question-text mb-4 pa-3 bg-gray-100 rounded">
            <v-icon class="mr-2" size="20">mdi-comment-question</v-icon>
            <strong>{{ lastSearchQuery }}</strong>
          </div>

          <div class="answer-text">
            <v-icon class="mr-2 mb-1" size="20" color="primary">mdi-lightbulb</v-icon>
            <div v-html="formatAnswer(intelligentAnswer.answer)" class="ml-7"></div>
          </div>

          <!-- Model Info -->
          <v-alert
            v-if="intelligentAnswer.model"
            type="info"
            variant="tonal"
            density="compact"
            class="mt-4"
          >
            <v-icon left>mdi-chip</v-icon>
            Powered by {{ intelligentAnswer.model }}
          </v-alert>
        </v-card-text>

        <v-card-actions class="px-6 pb-4">
          <v-btn outlined small @click="copyAnswer">
            <v-icon left small>mdi-content-copy</v-icon>
            Copy Answer
          </v-btn>
          <v-btn outlined small @click="exportAnswer">
            <v-icon left small>mdi-download</v-icon>
            Export
          </v-btn>
          <v-spacer></v-spacer>
          <v-btn text small @click="showSources = !showSources">
            <v-icon left small>mdi-file-document-multiple</v-icon>
            {{ showSources ? 'Hide' : 'Show' }} Sources ({{ intelligentAnswer.sources.length }})
          </v-btn>
        </v-card-actions>

        <!-- Sources -->
        <v-expand-transition>
          <div v-if="showSources" class="px-6 pb-6">
            <v-divider class="mb-4"></v-divider>
            <h4 class="text-subtitle-1 font-weight-bold mb-3">Source Documents</h4>
            <v-list class="bg-gray-50 rounded">
              <v-list-item
                v-for="(source, index) in intelligentAnswer.sources"
                :key="index"
                class="mb-2"
              >
                <v-list-item-content>
                  <div class="d-flex align-start">
                    <v-chip size="small" color="primary" class="mr-3">{{ index + 1 }}</v-chip>
                    <div class="flex-grow-1">
                      <div class="text-subtitle-2 font-weight-bold">{{ source.requirement_category || 'General' }}</div>
                      <div class="text-body-2 text-gray-700 mt-1">{{ source.requirement }}</div>
                      <div class="d-flex gap-2 mt-2">
                        <v-chip size="x-small" variant="outlined">{{ source.product }}</v-chip>
                        <v-chip size="x-small" variant="outlined">Score: {{ ((source.relevance_score || source.score || 0) * 100).toFixed(1) }}%</v-chip>
                      </div>
                    </div>
                  </div>
                </v-list-item-content>
              </v-list-item>
            </v-list>
          </div>
        </v-expand-transition>
      </v-card>

      <!-- Follow-up Question -->
      <v-card class="mb-6">
        <v-card-text class="pa-4">
          <v-text-field
            v-model="followUpQuestion"
            placeholder="Ask a follow-up question..."
            prepend-inner-icon="mdi-comment-plus"
            variant="outlined"
            density="compact"
            hide-details
            @keyup.enter="askFollowUp"
          >
            <template v-slot:append>
              <v-btn
                color="primary"
                size="small"
                @click="askFollowUp"
                :loading="loadingFollowUp"
                :disabled="!followUpQuestion"
              >
                Ask
              </v-btn>
            </template>
          </v-text-field>
        </v-card-text>
      </v-card>
    </div>

    <!-- Search Results (Search Mode) -->
    <div v-if="hasSearched && searchMode === 'search' && searchResults.length > 0">
      <div class="mb-4 d-flex justify-space-between align-center">
        <p class="text-body-1">
          Found <strong>{{ totalResults }}</strong> results
        </p>
        <v-btn text small color="primary" @click="exportResults">
          <v-icon left small>mdi-download</v-icon>
          Export
        </v-btn>
      </div>

      <v-card>
        <v-list class="py-0">
          <template v-for="(result, index) in searchResults" :key="result.id">
            <v-list-item class="py-4">
              <v-list-item-content>
                <div class="d-flex align-start">
                  <div class="mr-4 text-center">
                    <v-chip :color="getScoreColor(result.score)" size="small" dark>
                      {{ (result.score * 100).toFixed(0) }}%
                    </v-chip>
                  </div>
                  <div class="flex-grow-1">
                    <div class="d-flex gap-2 mb-2">
                      <v-chip size="small" color="primary">{{ result.payload.product }}</v-chip>
                      <v-chip size="small" variant="outlined">{{ result.payload.requirement_category }}</v-chip>
                    </div>
                    <p class="text-body-2 mb-2">{{ result.payload.requirement }}</p>
                    <v-btn
                      text
                      x-small
                      color="primary"
                      @click="toggleExpand(result.id)"
                    >
                      {{ expandedItems.includes(result.id) ? 'Show Less' : 'Show More' }}
                    </v-btn>
                    <v-expand-transition>
                      <div v-if="expandedItems.includes(result.id)" class="mt-3 pa-3 bg-gray-50 rounded">
                        <pre class="text-caption">{{ JSON.stringify(result.payload, null, 2) }}</pre>
                      </div>
                    </v-expand-transition>
                  </div>
                </div>
              </v-list-item-content>
            </v-list-item>
            <v-divider v-if="index < searchResults.length - 1" :key="`div-${index}`"></v-divider>
          </template>
        </v-list>
      </v-card>
    </div>

    <!-- Suggested Questions -->
    <v-card v-if="!hasSearched" class="pa-8">
      <div class="text-center mb-6">
        <v-icon size="64" color="primary">mdi-help-circle</v-icon>
        <h3 class="text-h6 mt-4 mb-2">Ask Me Anything About Your RFPs</h3>
        <p class="text-body-2 text-gray-600">
          Try these example questions or ask your own
        </p>
      </div>

      <div class="suggested-questions">
        <h4 class="text-subtitle-2 mb-3 text-gray-700">Suggested Questions:</h4>
        <v-chip-group column>
          <v-chip
            v-for="(question, index) in suggestedQuestions"
            :key="index"
            @click="searchQuery = question; performSearch()"
            class="ma-1"
            variant="outlined"
            color="primary"
          >
            <v-icon left size="small">mdi-lightbulb-on</v-icon>
            {{ question }}
          </v-chip>
        </v-chip-group>
      </div>
    </v-card>

    <!-- No Results -->
    <v-card v-if="hasSearched && !intelligentAnswer && searchResults.length === 0" class="pa-12 text-center">
      <v-icon size="64" color="gray">mdi-magnify-close</v-icon>
      <h3 class="text-h6 mt-4 mb-2">No results found</h3>
      <p class="text-body-2 text-gray-600">Try adjusting your query or filters</p>
    </v-card>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'IntelligentSearch',
  computed: {
    apiUrl() {
      return process.env.VUE_APP_API_URL || 'http://localhost:5000/api'
    }
  },
  data() {
    return {
      searchMode: 'intelligent',  // 'intelligent' or 'search'
      searchQuery: '',
      lastSearchQuery: '',
      followUpQuestion: '',
      loading: false,
      loadingFollowUp: false,
      hasSearched: false,
      showFilters: false,
      showAISettings: false,
      showSources: false,
      expandedItems: [],
      
      // AI Settings
      aiSettings: {
        temperature: 0.3,
        top_n: 5,
        max_tokens: 1000
      },
      
      // Filters
      filters: {
        products: [],
        response_categories: [],
        requirement_category: []
      },
      
      // Results
      intelligentAnswer: null,
      searchResults: [],
      totalResults: 0,
      conversationHistory: [],
      
      // Options
      availableProducts: ['MLC', 'EPLC', 'Integration', 'Mobile Banking', 'Internet Banking'],
      responseCategories: ['Readily Available', 'Configuration', 'Customization', 'Not Available'],
      requirementCategories: ['Functional', 'Technical', 'Security', 'Performance', 'Integration'],
      
      suggestedQuestions: []
    }
  },
  
  mounted() {
    this.loadSuggestedQuestions()
  },
  
  methods: {
    async performSearch() {
      if (!this.searchQuery || this.searchQuery.trim().length < 3) {
        return
      }
      
      this.loading = true
      this.hasSearched = true
      this.lastSearchQuery = this.searchQuery
      
      try {
        if (this.searchMode === 'intelligent') {
          await this.performIntelligentSearch()
        } else {
          await this.performVectorSearch()
        }
      } catch (error) {
        console.error('Search error:', error)
        this.$store.dispatch('showNotification', {
          message: `Search failed: ${error.message}`,
          type: 'error'
        })
      } finally {
        this.loading = false
      }
    },
    
    async performIntelligentSearch() {
      const response = await axios.post(`${this.apiUrl}/search/ask`, {
        question: this.searchQuery,
        filters: this.buildFilters(),
        ...this.aiSettings
      })
      
      this.intelligentAnswer = response.data
      
      // Add to conversation history
      this.conversationHistory.push({
        question: this.searchQuery,
        answer: this.intelligentAnswer.answer
      })
      
      this.searchQuery = ''
    },
    
    async performVectorSearch() {
      const response = await axios.post(`${this.apiUrl}/search/query`, {
        query: this.searchQuery,
        top_n: 20,
        filters: this.buildFilters()
      })
      
      this.searchResults = response.data.results
      this.totalResults = response.data.total_results
      this.searchQuery = ''
    },
    
    async askFollowUp() {
      if (!this.followUpQuestion) return
      
      this.loadingFollowUp = true
      
      try {
        const response = await axios.post(`${this.apiUrl}/search/follow-up`, {
          question: this.followUpQuestion,
          conversation_history: this.conversationHistory,
          filters: this.buildFilters()
        })
        
        this.intelligentAnswer = response.data
        this.lastSearchQuery = this.followUpQuestion
        
        this.conversationHistory.push({
          question: this.followUpQuestion,
          answer: this.intelligentAnswer.answer
        })
        
        this.followUpQuestion = ''
      } catch (error) {
        console.error('Follow-up error:', error)
      } finally {
        this.loadingFollowUp = false
      }
    },
    
    async loadSuggestedQuestions() {
      try {
        const response = await axios.get(`${this.apiUrl}/search/suggestions`)
        this.suggestedQuestions = response.data.suggestions
      } catch (error) {
        console.error('Failed to load suggestions:', error)
        this.suggestedQuestions = [
          'What are the main technical requirements?',
          'List all integration requirements',
          'What are the security requirements?',
          'Summarize the fraud detection specifications',
          'What AI/ML capabilities are required?'
        ]
      }
    },
    
    buildFilters() {
      const filters = {}
      if (this.filters.products.length > 0) {
        filters.product = this.filters.products
      }
      if (this.filters.response_categories.length > 0) {
        filters.response_category = this.filters.response_categories
      }
      if (this.filters.requirement_category.length > 0) {
        filters.requirement_category = this.filters.requirement_category
      }
      return filters
    },
    
    formatAnswer(answer) {
      // Convert markdown-style formatting to HTML
      return answer
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\n\n/g, '<br><br>')
        .replace(/\n- /g, '<br>• ')
        .replace(/\n\d+\. /g, '<br>$&')
    },
    
    getModeColor(mode) {
      const colors = {
        'intelligent': 'success',
        'search-only': 'warning',
        'no-results': 'error',
        'error': 'error'
      }
      return colors[mode] || 'gray'
    },
    
    getConfidenceColor(confidence) {
      if (confidence >= 0.8) return 'success'
      if (confidence >= 0.6) return 'warning'
      return 'error'
    },
    
    getScoreColor(score) {
      if (score >= 0.7) return 'success'
      if (score >= 0.5) return 'warning'
      return 'error'
    },
    
    toggleExpand(id) {
      const index = this.expandedItems.indexOf(id)
      if (index > -1) {
        this.expandedItems.splice(index, 1)
      } else {
        this.expandedItems.push(id)
      }
    },
    
    clearSearch() {
      this.searchQuery = ''
    },
    
    copyAnswer() {
      navigator.clipboard.writeText(this.intelligentAnswer.answer)
      this.$store.dispatch('showNotification', {
        message: 'Answer copied to clipboard',
        type: 'success'
      })
    },
    
    exportAnswer() {
      const data = {
        question: this.lastSearchQuery,
        answer: this.intelligentAnswer.answer,
        sources: this.intelligentAnswer.sources,
        mode: this.intelligentAnswer.mode,
        confidence: this.intelligentAnswer.confidence,
        timestamp: new Date().toISOString()
      }
      
      const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `rfp-qa-${Date.now()}.json`
      a.click()
      URL.revokeObjectURL(url)
    },
    
    exportResults() {
      const blob = new Blob([JSON.stringify(this.searchResults, null, 2)], { type: 'application/json' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `search-results-${Date.now()}.json`
      a.click()
      URL.revokeObjectURL(url)
    }
  }
}
</script>

<style scoped>
.bg-gradient-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.bg-gray-50 {
  background-color: #f9fafb;
}

.bg-gray-100 {
  background-color: #f3f4f6;
}

.text-gray-600 {
  color: #6b7280;
}

.text-gray-700 {
  color: #374151;
}

.answer-text {
  font-size: 15px;
  line-height: 1.6;
}

.question-text {
  font-size: 14px;
  border-left: 3px solid #667eea;
}

.mode-toggle {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.suggested-questions {
  max-width: 900px;
  margin: 0 auto;
}

pre {
  white-space: pre-wrap;
  word-wrap: break-word;
}
</style>
