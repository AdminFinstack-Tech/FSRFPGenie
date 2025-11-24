import { createStore } from 'vuex'
import axios from 'axios'

const API_URL = process.env.VUE_APP_API_URL || 'http://localhost:5000/api'

export default createStore({
  state: {
    documents: [],
    searchResults: [],
    templates: [],
    currentDocument: null,
    stats: {
      totalDocuments: 0,
      totalRecords: 0,
      productDistribution: {}
    },
    loading: false
  },
  
  mutations: {
    SET_DOCUMENTS(state, documents) {
      state.documents = documents
    },
    SET_SEARCH_RESULTS(state, results) {
      state.searchResults = results
    },
    SET_TEMPLATES(state, templates) {
      state.templates = templates
    },
    SET_CURRENT_DOCUMENT(state, document) {
      state.currentDocument = document
    },
    SET_STATS(state, stats) {
      state.stats = stats
    },
    SET_LOADING(state, loading) {
      state.loading = loading
    }
  },
  
  actions: {
    async uploadDocument(_, { file, documentType, metadata, processingMode = 'professional' }) {
      const formData = new FormData()
      formData.append('file', file)
      formData.append('document_type', documentType)
      formData.append('metadata', JSON.stringify(metadata))
      formData.append('processing_mode', processingMode)  // Include processing mode
      
      const response = await axios.post(`${API_URL}/documents/upload`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      })
      
      return response.data
    },
    
    async getDocumentStatus(_, documentId) {
      const response = await axios.get(`${API_URL}/documents/${documentId}/status`)
      return response.data
    },
    
    async analyzeDocument(_, documentId) {
      const response = await axios.get(`${API_URL}/documents/${documentId}/analyze`)
      return response.data
    },
    
    async submitColumnMapping(_, { documentId, mappings, saveTemplate, templateName }) {
      const response = await axios.post(`${API_URL}/documents/${documentId}/mapping`, {
        mappings,
        save_template: saveTemplate,
        template_name: templateName
      })
      return response.data
    },
    
    async searchRAG({ commit }, { query, topN = 10, filters = {} }) {
      commit('SET_LOADING', true)
      try {
        const response = await axios.post(`${API_URL}/query`, {
          query,
          top_n: topN,
          filters
        })
        commit('SET_SEARCH_RESULTS', response.data.results)
        return response.data
      } finally {
        commit('SET_LOADING', false)
      }
    },
    
    async getTemplates({ commit }) {
      const response = await axios.get(`${API_URL}/templates`)
      commit('SET_TEMPLATES', response.data)
      return response.data
    },
    
    async getDocumentRecords(_, { documentId, page = 1, limit = 50 }) {
      const response = await axios.get(`${API_URL}/documents/${documentId}/records`, {
        params: { page, limit }
      })
      return response.data
    },
    
    async getStats({ commit }) {
      const response = await axios.get(`${API_URL}/stats`)
      commit('SET_STATS', response.data)
      return response.data
    },
    
    async checkHealth() {
      const response = await axios.get(`${API_URL}/health`)
      return response.data
    }
  },
  
  getters: {
    isLoading: state => state.loading,
    searchResults: state => state.searchResults,
    templates: state => state.templates,
    stats: state => state.stats
  }
})