<template>
  <div class="search-container">
    <!-- Enhanced Page Header with Stats -->
    <div class="page-header">
      <div class="header-content">
        <div class="header-main">
          <div class="title-section">
            <v-icon size="56" class="brain-icon">mdi-brain</v-icon>
            <div>
              <h1 class="header-title">Intelligent RFP Assistant</h1>
              <p class="header-subtitle">AI-Powered Document Analysis & Natural Language Search</p>
            </div>
          </div>
          
          <!-- Quick Stats -->
          <div class="quick-stats">
            <div class="stat-card">
              <v-icon color="white">mdi-file-document-multiple</v-icon>
              <div class="stat-info">
                <div class="stat-value">{{ stats.totalDocuments }}</div>
                <div class="stat-label">Documents</div>
              </div>
            </div>
            <div class="stat-card">
              <v-icon color="white">mdi-database</v-icon>
              <div class="stat-info">
                <div class="stat-value">{{ stats.totalRecords }}</div>
                <div class="stat-label">Records</div>
              </div>
            </div>
            <div class="stat-card">
              <v-icon color="white">mdi-magnify</v-icon>
              <div class="stat-info">
                <div class="stat-value">{{ stats.totalSearches }}</div>
                <div class="stat-label">Searches</div>
              </div>
            </div>
          </div>
        </div>

        <!-- Quick Actions -->
        <div class="quick-actions mt-4">
          <v-btn variant="outlined" color="white" size="small" @click="showSearchHistory = !showSearchHistory">
            <v-icon left small>mdi-history</v-icon>
            Search History
          </v-btn>
          <v-btn variant="outlined" color="white" size="small" @click="showBookmarks = !showBookmarks">
            <v-icon left small>mdi-bookmark</v-icon>
            Bookmarks ({{ bookmarks.length }})
          </v-btn>
          <v-btn variant="outlined" color="white" size="small" @click="exportAll">
            <v-icon left small>mdi-download</v-icon>
            Export All
          </v-btn>
        </div>
      </div>
    </div>

    <!-- Search History Drawer -->
    <v-expand-transition>
      <v-card v-if="showSearchHistory" class="mb-4" elevation="2">
        <v-card-title class="d-flex justify-space-between align-center">
          <span><v-icon left>mdi-history</v-icon>Recent Searches</span>
          <v-btn icon size="small" @click="clearSearchHistory">
            <v-icon>mdi-delete</v-icon>
          </v-btn>
        </v-card-title>
        <v-card-text>
          <v-chip-group column>
            <v-chip
              v-for="(query, index) in searchHistory"
              :key="index"
              @click="searchQuery = query; performSearch()"
              closable
              @click:close="removeFromHistory(index)"
            >
              <v-icon left small>mdi-magnify</v-icon>
              {{ query }}
            </v-chip>
          </v-chip-group>
          <p v-if="searchHistory.length === 0" class="text-grey text-center py-4">
            No search history yet
          </p>
        </v-card-text>
      </v-card>
    </v-expand-transition>

    <!-- AI Search Mode Selector with Animation -->
    <v-card class="mode-selector mb-6" elevation="3">
      <v-card-text class="pa-4">
        <div class="d-flex align-center justify-space-between flex-wrap">
          <div class="mode-info">
            <h3 class="text-h6 mb-1 d-flex align-center">
              <v-icon left color="primary">mdi-robot-excited</v-icon>
              Search Mode
            </h3>
            <p class="text-caption text-grey mb-0">{{ getModeDescription() }}</p>
          </div>
          <v-chip-group v-model="searchMode" mandatory class="mode-chips">
            <v-chip 
              value="intelligent" 
              :color="searchMode === 'intelligent' ? 'primary' : 'default'" 
              size="large"
              class="px-6 py-6 mode-chip"
            >
              <v-icon left>mdi-robot</v-icon>
              <div class="chip-content">
                <div class="chip-title">AI Intelligent</div>
                <div class="chip-subtitle">GPT-4o Powered</div>
              </div>
            </v-chip>
            <v-chip 
              value="keyword" 
              :color="searchMode === 'keyword' ? 'secondary' : 'default'"
              size="large"
              class="px-6 py-6 mode-chip"
            >
              <v-icon left>mdi-magnify</v-icon>
              <div class="chip-content">
                <div class="chip-title">Keyword Search</div>
                <div class="chip-subtitle">Vector Similarity</div>
              </div>
            </v-chip>
          </v-chip-group>
        </div>
      </v-card-text>
    </v-card>

    <!-- Enhanced Search Bar -->
    <v-card class="search-card mb-6" elevation="4">
      <v-card-text class="pa-6">
        <div class="search-input-wrapper">
          <v-textarea
            v-model="searchQuery"
            :placeholder="getPlaceholder()"
            auto-grow
            rows="2"
            variant="outlined"
            density="comfortable"
            clearable
            @keydown.enter.exact="performSearch"
            @keydown.enter.shift.prevent
            class="enhanced-search-input"
            hide-details
          >
            <template v-slot:prepend-inner>
              <v-icon :color="searchMode === 'intelligent' ? 'primary' : 'secondary'" size="large">
                {{ searchMode === 'intelligent' ? 'mdi-chat-question' : 'mdi-magnify' }}
              </v-icon>
            </template>
          </v-textarea>
        </div>
        
        <div class="d-flex align-center justify-space-between mt-4 flex-wrap gap-2">
          <div class="d-flex gap-2 flex-wrap">
            <v-btn
              variant="text"
              size="small"
              @click="showFilters = !showFilters"
            >
              <v-icon left small>{{ showFilters ? 'mdi-chevron-up' : 'mdi-filter-variant' }}</v-icon>
              {{ showFilters ? 'Hide' : 'Show' }} Filters
            </v-btn>
            
            <v-btn
              variant="text"
              size="small"
              @click="voiceSearch"
              :disabled="!voiceSupported"
            >
              <v-icon left small>mdi-microphone</v-icon>
              Voice Search
            </v-btn>
          </div>
          
          <v-btn
            color="primary"
            size="x-large"
            @click="performSearch"
            :loading="loading"
            :disabled="!searchQuery"
            class="px-10 search-btn"
            elevation="2"
          >
            <v-icon left>{{ searchMode === 'intelligent' ? 'mdi-sparkles' : 'mdi-magnify' }}</v-icon>
            {{ searchMode === 'intelligent' ? 'Ask AI' : 'Search' }}
          </v-btn>
        </div>

        <!-- Advanced Filters -->
        <v-expand-transition>
          <div v-if="showFilters" class="mt-4 pt-4 border-t">
            <v-row>
              <v-col cols="12" md="3">
                <v-select
                  v-model="filters.products"
                  label="Filter by Products"
                  :items="availableProducts"
                  multiple
                  chips
                  closable-chips
                  clearable
                  density="compact"
                  variant="outlined"
                  prepend-inner-icon="mdi-package-variant"
                ></v-select>
              </v-col>
              <v-col cols="12" md="3">
                <v-select
                  v-model="filters.response_categories"
                  label="Response Category"
                  :items="responseCategories"
                  multiple
                  chips
                  closable-chips
                  clearable
                  density="compact"
                  variant="outlined"
                  prepend-inner-icon="mdi-tag"
                ></v-select>
              </v-col>
              <v-col cols="12" md="3">
                <v-select
                  v-model="resultLimit"
                  label="Max Results"
                  :items="[5, 10, 20, 50, 100]"
                  density="compact"
                  variant="outlined"
                  prepend-inner-icon="mdi-counter"
                ></v-select>
              </v-col>
              <v-col cols="12" md="3">
                <v-select
                  v-model="filters.confidence"
                  label="Min Confidence"
                  :items="['Any', '40%', '60%', '80%']"
                  density="compact"
                  variant="outlined"
                  prepend-inner-icon="mdi-speedometer"
                ></v-select>
              </v-col>
            </v-row>
          </div>
        </v-expand-transition>
      </v-card-text>
    </v-card>

    <!-- AI Answer Section with Confidence Meter -->
    <v-expand-transition>
      <div v-if="hasSearched && searchMode === 'intelligent' && aiAnswer">
        <v-card class="ai-answer-card mb-6" elevation="6">
          <div class="answer-header">
            <div class="d-flex align-center justify-space-between flex-wrap gap-3">
              <div class="d-flex align-center">
                <v-avatar :color="getConfidenceColor(aiAnswer.confidence)" size="50" class="mr-3">
                  <v-icon color="white" size="large">mdi-robot</v-icon>
                </v-avatar>
                <div>
                  <h3 class="text-h6 mb-1">AI Answer</h3>
                  <div class="d-flex align-center gap-2 flex-wrap">
                    <!-- Confidence Meter -->
                    <div class="confidence-meter">
                      <v-progress-linear
                        :model-value="aiAnswer.confidence * 100"
                        :color="getConfidenceColor(aiAnswer.confidence)"
                        height="8"
                        rounded
                        class="confidence-bar"
                      ></v-progress-linear>
                      <span class="confidence-text">
                        {{ Math.round(aiAnswer.confidence * 100) }}% Confidence
                      </span>
                    </div>
                    <v-chip size="x-small" color="primary" variant="outlined">
                      {{ aiAnswer.model || 'GPT-4o' }}
                    </v-chip>
                    <v-chip size="x-small" color="info" variant="outlined">
                      {{ aiAnswer.sources?.length || 0 }} Sources
                    </v-chip>
                  </div>
                </div>
              </div>
              
              <div class="d-flex gap-2">
                <v-tooltip text="Copy Answer" location="top">
                  <template v-slot:activator="{ props }">
                    <v-btn icon size="small" variant="tonal" @click="copyAnswer" v-bind="props">
                      <v-icon>mdi-content-copy</v-icon>
                    </v-btn>
                  </template>
                </v-tooltip>
                
                <v-tooltip text="Export to PDF" location="top">
                  <template v-slot:activator="{ props }">
                    <v-btn icon size="small" variant="tonal" @click="exportAnswer" v-bind="props">
                      <v-icon>mdi-file-pdf-box</v-icon>
                    </v-btn>
                  </template>
                </v-tooltip>
                
                <v-tooltip text="Bookmark" location="top">
                  <template v-slot:activator="{ props }">
                    <v-btn icon size="small" variant="tonal" @click="bookmarkAnswer" v-bind="props">
                      <v-icon>{{ isBookmarked ? 'mdi-bookmark' : 'mdi-bookmark-outline' }}</v-icon>
                    </v-btn>
                  </template>
                </v-tooltip>
                
                <v-tooltip text="Show/Hide Sources" location="top">
                  <template v-slot:activator="{ props }">
                    <v-btn 
                      icon 
                      size="small" 
                      variant="tonal" 
                      @click="toggleSourcesVisibility" 
                      v-bind="props"
                      :color="showSources ? 'primary' : 'default'"
                    >
                      <v-icon>{{ showSources ? 'mdi-eye' : 'mdi-eye-off' }}</v-icon>
                    </v-btn>
                  </template>
                </v-tooltip>
              </div>
            </div>
          </div>
          
          <v-card-text class="answer-content pa-6">
            <div class="answer-text" v-html="formattedAnswer"></div>
            
            <!-- Follow-up Questions -->
            <div v-if="suggestedQuestions.length > 0" class="mt-6 follow-up-section">
              <v-divider class="mb-4"></v-divider>
              <p class="text-subtitle-2 mb-3">
                <v-icon small class="mr-1" color="primary">mdi-help-circle</v-icon>
                <strong>Suggested follow-up questions:</strong>
              </p>
              <div class="d-flex flex-wrap gap-2">
                <v-chip
                  v-for="(question, index) in suggestedQuestions"
                  :key="index"
                  @click="askFollowUp(question)"
                  variant="outlined"
                  color="primary"
                  class="follow-up-chip"
                >
                  <v-icon left small>mdi-lightning-bolt</v-icon>
                  {{ question }}
                </v-chip>
              </div>
            </div>
          </v-card-text>
        </v-card>
      </div>
    </v-expand-transition>

    <!-- Source Documents Section with Enhanced Display -->
    <v-expand-transition>
      <div v-if="hasSearched && sourcesAvailable && showSources">
        <div class="sources-header mb-4 d-flex align-center justify-space-between">
          <div>
            <h2 class="text-h5 d-flex align-center">
              <v-icon class="mr-2" color="primary">mdi-file-document-multiple</v-icon>
              Source Documents
              <v-chip size="small" color="primary" class="ml-3">
                {{ totalResults }} Results
              </v-chip>
            </h2>
            <p class="text-body-2 text-grey mt-1 mb-0">
              {{ searchMode === 'intelligent' ? 'Documents used to generate the AI answer' : 'Most relevant matches based on semantic similarity' }}
            </p>
          </div>
          
          <div class="d-flex gap-2">
            <v-btn variant="outlined" size="small" @click="compareSelected" :disabled="selectedResults.length < 2">
              <v-icon left small>mdi-compare</v-icon>
              Compare ({{ selectedResults.length }})
            </v-btn>
            <v-btn variant="outlined" size="small" @click="exportSelected" :disabled="selectedResults.length === 0">
              <v-icon left small>mdi-download</v-icon>
              Export Selected
            </v-btn>
          </div>
        </div>

        <v-card v-if="searchResults.length > 0" class="sources-card" elevation="3">
          <v-list class="py-0">
            <template v-for="(result, index) in searchResults" :key="result.record_id">
              <v-list-item class="source-item py-4 px-4">
                <!-- Selection Checkbox -->
                <template v-slot:prepend>
                  <v-checkbox
                    v-model="selectedResults"
                    :value="result.record_id"
                    hide-details
                    density="compact"
                    class="mr-2"
                  ></v-checkbox>
                </template>

                <v-list-item-content>
                  <div class="d-flex align-start gap-4">
                    <!-- Relevance Score Indicator -->
                    <div class="relevance-indicator">
                      <v-progress-circular
                        :model-value="result.relevance_score * 100"
                        :size="70"
                        :width="7"
                        :color="getScoreColor(result.relevance_score)"
                        class="score-circle"
                      >
                        <div class="score-content">
                          <span class="score-text">{{ Math.round(result.relevance_score * 100) }}</span>
                          <span class="score-percent">%</span>
                        </div>
                      </v-progress-circular>
                      <p class="text-caption text-center mt-2 mb-0 font-weight-bold">Match Score</p>
                    </div>

                    <!-- Main Content -->
                    <div class="flex-grow-1">
                      <!-- Document Info Header with Sheet -->
                      <div class="document-header mb-3">
                        <div class="d-flex align-center flex-wrap gap-2 mb-2">
                          <v-icon color="primary">mdi-file-document</v-icon>
                          <strong class="text-subtitle-1">{{ result.file_name || result.rfp_name }}</strong>
                          
                          <!-- Sheet Name Badge (Prominent) -->
                          <v-chip
                            v-if="result.sheet_name"
                            size="small"
                            color="info"
                            variant="flat"
                            class="sheet-badge"
                          >
                            <v-icon left size="small">mdi-table-large</v-icon>
                            <strong>Sheet: {{ result.sheet_name }}</strong>
                          </v-chip>
                          
                          <v-chip size="x-small" variant="outlined">
                            <v-icon left size="x-small">mdi-bank</v-icon>
                            {{ result.bank_name }}
                          </v-chip>
                          
                          <v-chip size="x-small" variant="outlined">
                            <v-icon left size="x-small">mdi-calendar</v-icon>
                            {{ formatDate(result.date) }}
                          </v-chip>
                        </div>
                      </div>

                      <!-- Meta Tags -->
                      <div class="meta-tags mb-3">
                        <v-chip size="small" label class="mr-2" color="primary" variant="outlined">
                          <v-icon left size="small">mdi-package-variant</v-icon>
                          {{ result.product || 'General' }}
                        </v-chip>
                        
                        <v-chip
                          size="small"
                          label
                          :color="getResponseColor(result.response_category)"
                          class="mr-2"
                        >
                          <v-icon left size="small">mdi-tag</v-icon>
                          {{ result.response_category }}
                        </v-chip>

                        <v-chip
                          v-if="result.requirement_category"
                          size="small"
                          label
                          outlined
                          class="mr-2"
                          color="purple"
                        >
                          <v-icon left size="small">mdi-priority-high</v-icon>
                          {{ result.requirement_category }}
                        </v-chip>

                        <v-chip
                          v-if="result.effort_required"
                          size="small"
                          label
                          outlined
                          class="mr-2"
                          color="orange"
                        >
                          <v-icon left size="small">mdi-clock-outline</v-icon>
                          {{ result.effort_required }}
                        </v-chip>
                      </div>

                      <!-- Requirement Preview -->
                      <div class="requirement-preview mb-3">
                        <div class="requirement-content pa-4 rounded">
                          <p class="text-body-1 mb-0 requirement-text">
                            {{ truncateText(result.requirement, 300) }}
                          </p>
                        </div>
                        
                        <!-- Highlighted Match -->
                        <div v-if="result.highlight" class="highlight-box pa-3 rounded mt-3">
                          <p class="text-caption text-grey mb-1 d-flex align-center">
                            <v-icon size="small" class="mr-1">mdi-text-search</v-icon>
                            <strong>Matching excerpt:</strong>
                          </p>
                          <p class="text-body-2 highlight-text" v-html="result.highlight"></p>
                        </div>
                      </div>

                      <!-- Expandable Full Details -->
                      <v-expand-transition>
                        <div v-if="expandedItems.includes(result.record_id)" class="expanded-section">
                          <v-divider class="my-4"></v-divider>
                          
                          <div class="expanded-content pa-4 rounded">
                            <!-- Full Sheet Information -->
                            <div v-if="result.sheet_name || result.file_name" class="sheet-info-section mb-4">
                              <h4 class="text-subtitle-2 font-weight-bold mb-2 d-flex align-center">
                                <v-icon small class="mr-2" color="info">mdi-file-excel</v-icon>
                                Document Information
                              </h4>
                              <v-list density="compact" class="bg-transparent">
                                <v-list-item v-if="result.file_name">
                                  <template v-slot:prepend>
                                    <v-icon size="small">mdi-file</v-icon>
                                  </template>
                                  <v-list-item-title>File Name</v-list-item-title>
                                  <v-list-item-subtitle>{{ result.file_name }}</v-list-item-subtitle>
                                </v-list-item>
                                <v-list-item v-if="result.sheet_name">
                                  <template v-slot:prepend>
                                    <v-icon size="small">mdi-table</v-icon>
                                  </template>
                                  <v-list-item-title>Sheet Name</v-list-item-title>
                                  <v-list-item-subtitle>{{ result.sheet_name }}</v-list-item-subtitle>
                                </v-list-item>
                                <v-list-item v-if="result.row_number">
                                  <template v-slot:prepend>
                                    <v-icon size="small">mdi-table-row</v-icon>
                                  </template>
                                  <v-list-item-title>Row Number</v-list-item-title>
                                  <v-list-item-subtitle>Row {{ result.row_number }}</v-list-item-subtitle>
                                </v-list-item>
                              </v-list>
                            </div>

                            <h4 class="text-subtitle-2 font-weight-bold mb-3 d-flex align-center">
                              <v-icon small class="mr-2">mdi-text-box</v-icon>
                              Full Requirement
                            </h4>
                            <div class="requirement-box pa-4 rounded mb-4">
                              <p class="text-body-1 requirement-text mb-0">{{ cleanRequirement(result.requirement) }}</p>
                            </div>
                            
                            <div v-if="result.comments" class="mb-4">
                              <h4 class="text-subtitle-2 font-weight-bold mb-2 d-flex align-center">
                                <v-icon small class="mr-2">mdi-comment-text</v-icon>
                                Comments
                              </h4>
                              <div class="comments-box pa-3 rounded">
                                <p class="text-body-2">{{ result.comments }}</p>
                              </div>
                            </div>

                            <!-- Action Buttons -->
                            <div class="d-flex gap-2 mt-4 flex-wrap">
                              <v-btn size="small" variant="outlined" color="primary" @click="copyText(result.requirement)">
                                <v-icon left size="small">mdi-content-copy</v-icon>
                                Copy Text
                              </v-btn>
                              <v-btn size="small" variant="outlined" color="primary" @click="bookmarkResult(result)">
                                <v-icon left size="small">mdi-bookmark-outline</v-icon>
                                Bookmark
                              </v-btn>
                              <v-btn size="small" variant="outlined" color="primary" @click="searchSimilar(result)">
                                <v-icon left size="small">mdi-magnify-plus</v-icon>
                                Find Similar
                              </v-btn>
                              <v-btn size="small" variant="outlined" color="success" @click="generateResponse(result)">
                                <v-icon left size="small">mdi-robot</v-icon>
                                AI Generate Response
                              </v-btn>
                            </div>
                          </div>
                        </div>
                      </v-expand-transition>

                      <!-- Toggle Button -->
                      <v-btn
                        variant="text"
                        size="small"
                        color="primary"
                        @click="toggleExpand(result.record_id)"
                        class="mt-3"
                      >
                        <v-icon left size="small">
                          {{ expandedItems.includes(result.record_id) ? 'mdi-chevron-up' : 'mdi-chevron-down' }}
                        </v-icon>
                        {{ expandedItems.includes(result.record_id) ? 'Show Less' : 'Show Full Details' }}
                      </v-btn>
                    </div>
                  </div>
                </v-list-item-content>
              </v-list-item>
              
              <v-divider
                v-if="index < searchResults.length - 1"
                :key="`divider-${index}`"
              ></v-divider>
            </template>
          </v-list>
        </v-card>

        <!-- No Results -->
        <v-card v-else class="empty-state pa-12 text-center" elevation="2">
          <v-icon size="80" color="grey-lighten-1">mdi-file-search</v-icon>
          <h3 class="text-h6 mt-4 mb-2">No Matching Documents Found</h3>
          <p class="text-body-2 text-grey mb-4">
            We couldn't find any documents matching your search criteria.
          </p>
          <v-btn color="primary" variant="outlined" @click="clearSearch">
            <v-icon left>mdi-refresh</v-icon>
            Try New Search
          </v-btn>
        </v-card>
      </div>
    </v-expand-transition>

    <!-- Initial Welcome State -->
    <v-card v-if="!hasSearched" class="welcome-card pa-12 text-center" elevation="3">
      <v-icon size="100" color="primary" class="pulse-animation">mdi-comment-question</v-icon>
      <h3 class="text-h4 mt-6 mb-3 gradient-text">Ask Anything About Your RFPs</h3>
      <p class="text-h6 text-grey mb-8">
        Use natural language to search through your RFP documents and get instant AI-powered answers
      </p>
      
      <!-- Example Queries -->
      <div class="mx-auto" style="max-width: 900px;">
        <p class="text-subtitle-1 mb-4 font-weight-bold">
          <v-icon class="mr-2" color="primary">mdi-lightbulb-on</v-icon>
          Try these example queries:
        </p>
        <div class="example-grid">
          <v-card
            v-for="(example, index) in exampleQueries"
            :key="index"
            @click="searchQuery = example; performSearch()"
            class="example-card pa-4"
            elevation="2"
            hover
          >
            <v-icon color="primary" size="large" class="mb-2">mdi-lightning-bolt-circle</v-icon>
            <p class="text-body-2 mb-0">{{ example }}</p>
          </v-card>
        </div>
      </div>
    </v-card>
  </div>
</template>

<script>
import { format } from 'date-fns'
import axios from 'axios'
import { marked } from 'marked'

export default {
  name: 'SearchView',
  data() {
    return {
      searchMode: 'intelligent',
      searchQuery: '',
      lastSearchQuery: '',
      showFilters: false,
      showSources: true, // Show sources by default
      loading: false,
      hasSearched: false,
      expandedItems: [],
      selectedResults: [],
      isBookmarked: false,
      showSearchHistory: false,
      showBookmarks: false,
      
      aiAnswer: null,
      suggestedQuestions: [],
      
      filters: {
        products: [],
        response_categories: [],
        confidence: 'Any'
      },
      resultLimit: 10,
      totalResults: 0,
      
      searchResults: [],
      searchHistory: [],
      bookmarks: [],
      
      stats: {
        totalDocuments: 0,
        totalRecords: 0,
        totalSearches: 0
      },
      
      availableProducts: ['MLC', 'EPLC', 'Integration', 'Mobile Banking', 'Internet Banking', 'General', 'Core Banking', 'APIs'],
      responseCategories: ['Readily Available', 'Configuration', 'Customization', 'Not Available', 'Pending Review'],
      
      exampleQueries: [
        'What are the security and authentication requirements?',
        'Describe the reporting and analytics capabilities needed',
        'What integration requirements exist for core banking systems?',
        'List all the mobile banking features required in the RFP',
        'What compliance and regulatory requirements must be met?',
        'Explain the disaster recovery and backup requirements'
      ],
      
      voiceSupported: 'webkitSpeechRecognition' in window || 'SpeechRecognition' in window
    }
  },
  
  computed: {
    sourcesAvailable() {
      return this.searchResults && this.searchResults.length > 0
    },
    formattedAnswer() {
      if (!this.aiAnswer || !this.aiAnswer.answer) return ''
      return marked(this.aiAnswer.answer)
    }
  },
  
  mounted() {
    this.loadStats()
    this.loadSearchHistory()
    this.loadBookmarks()
  },
  
  methods: {
    async performSearch() {
      if (!this.searchQuery || this.searchQuery.trim().length < 3) {
        this.$toast.warning('Please enter at least 3 characters')
        return
      }
      
      this.loading = true
      this.hasSearched = true
      this.lastSearchQuery = this.searchQuery
      this.expandedItems = []
      this.selectedResults = []
      this.aiAnswer = null
      this.searchResults = []
      this.showSources = true // Always show sources after search
      
      // Add to search history
      this.addToSearchHistory(this.searchQuery)
      
      try {
        if (this.searchMode === 'intelligent') {
          // AI Intelligent Search
          const response = await axios.post('/api/search/ask', {
            question: this.searchQuery,
            filters: this.filters,
            max_context_docs: this.resultLimit,
            temperature: 0.7,
            max_answer_length: 1000
          })
          
          this.aiAnswer = response.data
          this.searchResults = response.data.sources || []
          this.totalResults = this.searchResults.length
          
          // Generate suggested follow-up questions
          this.generateFollowUpQuestions()
          
        } else {
          // Keyword Search
          const response = await axios.post('/api/search', {
            query: this.searchQuery,
            top_n: this.resultLimit,
            filters: this.filters
          })
          
          this.searchResults = response.data.results || []
          this.totalResults = response.data.total_results || 0
        }
        
        if (this.totalResults === 0) {
          this.$toast.info('No results found. Try different keywords.')
        } else {
          this.$toast.success(`Found ${this.totalResults} relevant results`)
        }
        
        // Update stats
        this.stats.totalSearches++
        
      } catch (error) {
        console.error('Search error:', error)
        this.$toast.error('Search failed. Please try again.')
      } finally {
        this.loading = false
      }
    },
    
    toggleSourcesVisibility() {
      this.showSources = !this.showSources
      this.$toast.info(this.showSources ? 'Sources visible' : 'Sources hidden')
    },
    
    getModeDescription() {
      return this.searchMode === 'intelligent' 
        ? 'Get AI-powered answers with natural language understanding'
        : 'Find documents using keyword-based vector similarity search'
    },
    
    getPlaceholder() {
      if (this.searchMode === 'intelligent') {
        return 'Ask a question: What are the fraud detection requirements? How does the system handle multi-currency?'
      }
      return 'Enter keywords: authentication, reporting, integration...'
    },
    
    generateFollowUpQuestions() {
      const question = this.searchQuery.toLowerCase()
      this.suggestedQuestions = []
      
      if (question.includes('requirement') || question.includes('security') || question.includes('authentication')) {
        this.suggestedQuestions.push('What are the technical specifications?')
        this.suggestedQuestions.push('Are there any compliance requirements?')
        this.suggestedQuestions.push('What encryption standards are required?')
      } else if (question.includes('integration') || question.includes('api')) {
        this.suggestedQuestions.push('What are the API specifications?')
        this.suggestedQuestions.push('Which systems need to be integrated?')
        this.suggestedQuestions.push('What data formats are supported?')
      } else {
        this.suggestedQuestions = [
          'Can you provide more technical details?',
          'What are the implementation requirements?',
          'Are there any related features or dependencies?'
        ]
      }
    },
    
    askFollowUp(question) {
      this.searchQuery = question
      this.performSearch()
    },
    
    voiceSearch() {
      if (!this.voiceSupported) {
        this.$toast.warning('Voice search not supported in your browser')
        return
      }
      
      const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)()
      recognition.lang = 'en-US'
      recognition.interimResults = false
      
      recognition.onresult = (event) => {
        this.searchQuery = event.results[0][0].transcript
        this.$toast.success('Voice captured! Click Search to continue.')
      }
      
      recognition.onerror = () => {
        this.$toast.error('Voice recognition failed')
      }
      
      recognition.start()
      this.$toast.info('Listening... Speak now')
    },
    
    addToSearchHistory(query) {
      if (!this.searchHistory.includes(query)) {
        this.searchHistory.unshift(query)
        if (this.searchHistory.length > 10) {
          this.searchHistory.pop()
        }
        localStorage.setItem('searchHistory', JSON.stringify(this.searchHistory))
      }
    },
    
    loadSearchHistory() {
      const history = localStorage.getItem('searchHistory')
      if (history) {
        this.searchHistory = JSON.parse(history)
      }
    },
    
    clearSearchHistory() {
      this.searchHistory = []
      localStorage.removeItem('searchHistory')
      this.$toast.success('Search history cleared')
    },
    
    removeFromHistory(index) {
      this.searchHistory.splice(index, 1)
      localStorage.setItem('searchHistory', JSON.stringify(this.searchHistory))
    },
    
    bookmarkAnswer() {
      if (!this.aiAnswer) return
      
      const bookmark = {
        id: Date.now(),
        query: this.lastSearchQuery,
        answer: this.aiAnswer.answer,
        confidence: this.aiAnswer.confidence,
        timestamp: new Date().toISOString()
      }
      
      this.bookmarks.unshift(bookmark)
      localStorage.setItem('bookmarks', JSON.stringify(this.bookmarks))
      this.isBookmarked = true
      this.$toast.success('Answer bookmarked!')
    },
    
    bookmarkResult(result) {
      // eslint-disable-next-line no-unused-vars
      const bookmark = {
        id: Date.now(),
        type: 'result',
        ...result,
        timestamp: new Date().toISOString()
      }
      
      this.bookmarks.unshift(bookmark)
      localStorage.setItem('bookmarks', JSON.stringify(this.bookmarks))
      this.$toast.success('Result bookmarked!')
    },
    
    loadBookmarks() {
      const bookmarks = localStorage.getItem('bookmarks')
      if (bookmarks) {
        this.bookmarks = JSON.parse(bookmarks)
      }
    },
    
    async loadStats() {
      try {
        const response = await axios.get('/api/stats')
        this.stats = response.data
      } catch (error) {
        console.error('Failed to load stats:', error)
      }
    },
    
    clearSearch() {
      this.searchQuery = ''
      this.hasSearched = false
      this.lastSearchQuery = ''
      this.aiAnswer = null
      this.searchResults = []
      this.expandedItems = []
      this.selectedResults = []
      this.suggestedQuestions = []
      this.isBookmarked = false
    },
    
    toggleExpand(recordId) {
      const index = this.expandedItems.indexOf(recordId)
      if (index > -1) {
        this.expandedItems.splice(index, 1)
      } else {
        this.expandedItems.push(recordId)
      }
    },
    
    async copyText(text) {
      try {
        await navigator.clipboard.writeText(text)
        this.$toast.success('Copied to clipboard!')
      } catch (err) {
        this.$toast.error('Failed to copy')
      }
    },
    
    async copyAnswer() {
      if (this.aiAnswer && this.aiAnswer.answer) {
        await this.copyText(this.aiAnswer.answer)
      }
    },
    
    exportAnswer() {
      this.$toast.info('Exporting to PDF... (Coming soon)')
    },
    
    // eslint-disable-next-line no-unused-vars
    exportAll() {
      this.$toast.info('Export all functionality coming soon')
    },
    
    compareSelected() {
      if (this.selectedResults.length < 2) {
        this.$toast.warning('Please select at least 2 results to compare')
        return
      }
      this.$toast.info('Comparison view coming soon')
    },
    
    exportSelected() {
      if (this.selectedResults.length === 0) {
        this.$toast.warning('Please select results to export')
        return
      }
      this.$toast.info(`Exporting ${this.selectedResults.length} results... (Coming soon)`)
    },
    
    searchSimilar(result) {
      this.searchQuery = result.requirement.substring(0, 100)
      this.searchMode = 'keyword'
      this.performSearch()
    },
    
    // eslint-disable-next-line no-unused-vars
    generateResponse(_result) {
      this.$toast.info('AI response generation coming soon')
    },
    
    cleanRequirement(text) {
      if (!text) return ''
      
      // Remove "Unnamed: N:" patterns and clean up the text
      let cleaned = text.replace(/Unnamed:\s*\d+:\s*/g, '')
      
      // Split by pipe symbols and extract meaningful content
      const parts = cleaned.split('|').map(p => p.trim()).filter(p => p.length > 0)
      
      // If we have multiple parts, join them with better formatting
      if (parts.length > 1) {
        return parts.join(' • ')
      }
      
      return cleaned.trim()
    },
    
    truncateText(text, length) {
      if (!text) return ''
      // Clean first, then truncate
      const cleaned = this.cleanRequirement(text)
      if (cleaned.length <= length) return cleaned
      return cleaned.substring(0, length) + '...'
    },
    
    formatDate(dateString) {
      if (!dateString) return 'N/A'
      try {
        return format(new Date(dateString), 'MMM d, yyyy')
      } catch {
        return dateString
      }
    },
    
    getScoreColor(score) {
      if (score >= 0.8) return 'success'
      if (score >= 0.6) return 'info'
      if (score >= 0.4) return 'warning'
      return 'error'
    },
    
    getConfidenceColor(confidence) {
      if (confidence >= 0.8) return 'success'
      if (confidence >= 0.6) return 'warning'
      return 'error'
    },
    
    getResponseColor(category) {
      const colors = {
        'Readily Available': 'success',
        'Configuration': 'info',
        'Customization': 'warning',
        'Not Available': 'error',
        'Pending Review': 'grey'
      }
      return colors[category] || 'grey'
    }
  }
}
</script>

<style scoped>
.search-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 24px;
}

/* Enhanced Header */
.page-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
  border-radius: 20px;
  padding: 40px;
  margin-bottom: 32px;
  color: white;
  box-shadow: 0 20px 60px rgba(102, 126, 234, 0.4);
  position: relative;
  overflow: hidden;
}

.page-header::before {
  content: '';
  position: absolute;
  top: -50%;
  right: -50%;
  width: 200%;
  height: 200%;
  background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
  animation: rotate 20s linear infinite;
}

@keyframes rotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.header-content {
  position: relative;
  z-index: 1;
}

.header-main {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  flex-wrap: wrap;
  gap: 24px;
}

.title-section {
  display: flex;
  align-items: center;
  gap: 20px;
}

.brain-icon {
  animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.1); }
}

.header-title {
  font-size: 2.5rem;
  font-weight: 800;
  margin: 0;
  line-height: 1.2;
  text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
}

.header-subtitle {
  font-size: 1.1rem;
  opacity: 0.95;
  margin: 8px 0 0 0;
}

.quick-stats {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
}

.stat-card {
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(10px);
  border-radius: 12px;
  padding: 16px 24px;
  display: flex;
  align-items: center;
  gap: 12px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  transition: transform 0.2s ease;
}

.stat-card:hover {
  transform: translateY(-4px);
  background: rgba(255, 255, 255, 0.2);
}

.stat-info {
  text-align: left;
}

.stat-value {
  font-size: 1.75rem;
  font-weight: 700;
  line-height: 1;
}

.stat-label {
  font-size: 0.75rem;
  opacity: 0.9;
  margin-top: 4px;
}

.quick-actions {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

/* Mode Selector */
.mode-selector {
  border-radius: 16px !important;
  border: 2px solid #e0e0e0;
  transition: all 0.3s ease;
}

.mode-selector:hover {
  border-color: #667eea;
  box-shadow: 0 8px 24px rgba(102, 126, 234, 0.2);
}

.mode-info {
  flex: 1;
  min-width: 250px;
}

.mode-chips {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.mode-chip {
  transition: all 0.3s ease;
  cursor: pointer;
}

.mode-chip:hover {
  transform: translateY(-2px);
}

.chip-content {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  margin-left: 8px;
}

.chip-title {
  font-weight: 600;
  font-size: 0.95rem;
}

.chip-subtitle {
  font-size: 0.7rem;
  opacity: 0.8;
}

/* Search Card */
.search-card {
  border-radius: 20px !important;
  border: 2px solid #f0f0f0;
  transition: all 0.3s ease;
}

.search-card:hover {
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15) !important;
  border-color: #667eea;
}

.enhanced-search-input >>> .v-field {
  border-radius: 16px;
  font-size: 1.15rem;
  border: 2px solid #e0e0e0;
  transition: border-color 0.3s ease;
}

.enhanced-search-input >>> .v-field:hover {
  border-color: #667eea;
}

.search-btn {
  font-weight: 600;
  letter-spacing: 0.5px;
  transition: all 0.3s ease;
}

.search-btn:hover {
  transform: translateY(-2px);
}

/* AI Answer Card */
.ai-answer-card {
  border-radius: 20px !important;
  border-left: 6px solid #667eea;
  overflow: hidden;
}

.answer-header {
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  padding: 24px;
}

.confidence-meter {
  display: flex;
  flex-direction: column;
  gap: 4px;
  min-width: 150px;
}

.confidence-bar {
  border-radius: 10px;
}

.confidence-text {
  font-size: 0.75rem;
  font-weight: 600;
  color: #666;
}

.answer-content {
  background: white;
}

.answer-text {
  font-size: 1.1rem;
  line-height: 1.9;
  color: #2d3748;
}

.answer-text >>> h3 {
  margin-top: 24px;
  margin-bottom: 16px;
  font-weight: 700;
  color: #667eea;
}

.answer-text >>> p {
  margin-bottom: 16px;
}

.answer-text >>> ul, .answer-text >>> ol {
  margin-left: 28px;
  margin-bottom: 16px;
}

.answer-text >>> li {
  margin-bottom: 10px;
}

.answer-text >>> strong {
  color: #667eea;
  font-weight: 700;
}

.answer-text >>> code {
  background: #f5f7fa;
  padding: 2px 6px;
  border-radius: 4px;
  font-family: 'Monaco', 'Courier New', monospace;
  font-size: 0.9em;
}

.follow-up-section {
  background: #f8f9fa;
  border-radius: 12px;
  padding: 16px;
}

.follow-up-chip {
  cursor: pointer;
  transition: all 0.2s ease;
}

.follow-up-chip:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

/* Sources Section */
.sources-header {
  padding: 16px 8px;
}

.sources-card {
  border-radius: 16px !important;
}

.source-item {
  transition: background-color 0.2s ease;
}

.source-item:hover {
  background-color: #f8f9fa;
}

.relevance-indicator {
  text-align: center;
  min-width: 90px;
}

.score-circle {
  position: relative;
}

.score-content {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.score-text {
  font-size: 20px;
  font-weight: 800;
  line-height: 1;
}

.score-percent {
  font-size: 10px;
  font-weight: 600;
  opacity: 0.8;
}

.document-header {
  background: linear-gradient(135deg, #f5f7fa 0%, #e8ecf1 100%);
  padding: 12px 16px;
  border-radius: 12px;
  border-left: 4px solid #667eea;
}

.sheet-badge {
  font-weight: 700 !important;
  letter-spacing: 0.5px;
  box-shadow: 0 2px 8px rgba(33, 150, 243, 0.3);
}

.meta-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.requirement-preview {
  padding: 16px 0;
}

.requirement-content {
  background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
  border: 2px solid #e3f2fd;
  border-left: 5px solid #2196F3;
  box-shadow: 0 2px 12px rgba(33, 150, 243, 0.1);
  transition: all 0.3s ease;
}

.requirement-content:hover {
  border-color: #2196F3;
  box-shadow: 0 4px 20px rgba(33, 150, 243, 0.2);
  transform: translateY(-2px);
}

.requirement-content .requirement-text {
  font-size: 1.05rem;
  line-height: 1.8;
  color: #2c3e50;
  font-weight: 400;
  letter-spacing: 0.3px;
}

.highlight-box {
  background: linear-gradient(135deg, #fff3cd 0%, #ffe69c 100%);
  border-left: 4px solid #ffc107;
  box-shadow: 0 2px 8px rgba(255, 193, 7, 0.2);
}

.highlight-text {
  margin: 0;
}

.highlight-text >>> strong {
  background: #ffeb3b;
  padding: 2px 6px;
  border-radius: 4px;
  font-weight: 700;
}

.expanded-section {
  animation: expandIn 0.3s ease;
}

@keyframes expandIn {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.expanded-content {
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  border: 2px solid #e0e0e0;
}

.sheet-info-section {
  background: white;
  border-radius: 12px;
  padding: 16px;
  border: 2px solid #2196F3;
}

.requirement-box {
  background: linear-gradient(135deg, #ffffff 0%, #fafbfc 100%);
  border: 2px solid #e1e8ed;
  border-left: 5px solid #667eea;
  box-shadow: 0 3px 15px rgba(102, 126, 234, 0.1);
  transition: all 0.3s ease;
}

.requirement-box:hover {
  border-color: #667eea;
  box-shadow: 0 5px 25px rgba(102, 126, 234, 0.15);
}

.requirement-box .requirement-text {
  font-size: 1.05rem;
  white-space: pre-wrap;
  line-height: 1.9;
  margin: 0;
  color: #2c3e50;
  font-weight: 400;
  letter-spacing: 0.3px;
}

.comments-box {
  background: #fff9c4;
  border-left: 4px solid #fdd835;
}

/* Welcome State */
.welcome-card {
  border-radius: 20px !important;
  margin-top: 60px;
  background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
}

.pulse-animation {
  animation: pulse 2s ease-in-out infinite;
}

.gradient-text {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.example-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 16px;
  margin-top: 24px;
}

.example-card {
  cursor: pointer;
  transition: all 0.3s ease;
  border: 2px solid #e0e0e0;
  text-align: center;
}

.example-card:hover {
  transform: translateY(-6px);
  box-shadow: 0 12px 32px rgba(102, 126, 234, 0.3) !important;
  border-color: #667eea;
}

/* Utility Classes */
.gap-2 {
  gap: 8px;
}

.border-t {
  border-top: 1px solid #e0e0e0;
}

/* Responsive Design */
@media (max-width: 960px) {
  .header-title {
    font-size: 2rem;
  }
  
  .quick-stats {
    width: 100%;
  }
  
  .stat-card {
    flex: 1;
    min-width: 120px;
  }
  
  .mode-chips {
    width: 100%;
  }
  
  .mode-chip {
    flex: 1;
  }
}

@media (max-width: 600px) {
  .search-container {
    padding: 16px;
  }
  
  .page-header {
    padding: 24px 20px;
  }
  
  .header-title {
    font-size: 1.5rem;
  }
  
  .quick-stats {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
  }
  
  .stat-card {
    flex-direction: column;
    text-align: center;
    padding: 12px;
  }
  
  .stat-value {
    font-size: 1.5rem;
  }
}
</style>
