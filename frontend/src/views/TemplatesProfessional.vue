<template>
  <div class="templates-professional">
    <!-- Page Header -->
    <div class="page-header">
      <h1 class="page-title">RFP Templates</h1>
      <p class="page-description">Manage and apply RFP response templates</p>
    </div>

    <!-- Controls Bar -->
    <div class="controls-bar">
      <div class="search-box">
        <v-icon size="20" color="#64748b">mdi-magnify</v-icon>
        <input 
          v-model="searchQuery" 
          type="text" 
          class="search-input"
          placeholder="Search templates..."
          @input="filterTemplates"
        />
      </div>
      
      <button class="btn-primary" @click="createTemplate">
        <v-icon size="18" left color="white">mdi-plus</v-icon>
        Create Template
      </button>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="loading-state">
      <v-progress-circular indeterminate color="#14b8a6" size="64"></v-progress-circular>
      <p class="loading-text">Loading templates...</p>
    </div>

    <!-- Empty State -->
    <div v-else-if="filteredTemplates.length === 0 && !loading" class="empty-state">
      <v-icon size="64" color="#cbd5e1">mdi-text-box-multiple-outline</v-icon>
      <p class="empty-title">{{ searchQuery ? 'No templates found' : 'No templates yet' }}</p>
      <p class="empty-subtitle">{{ searchQuery ? 'Try a different search' : 'Create your first template to get started' }}</p>
      <button v-if="!searchQuery" class="btn-primary" @click="createTemplate">
        <v-icon left color="white">mdi-plus</v-icon>
        Create Template
      </button>
    </div>

    <!-- Templates Grid -->
    <div v-else class="templates-grid">
      <div v-for="template in filteredTemplates" :key="template.id" class="template-card">
        <!-- Card Header -->
        <div class="card-header">
          <div class="template-icon">
            <v-icon size="24" color="#14b8a6">mdi-text-box-multiple</v-icon>
          </div>
          <div class="card-actions">
            <button class="action-btn" @click="editTemplate(template)" title="Edit">
              <v-icon size="18" color="#64748b">mdi-pencil</v-icon>
            </button>
            <button class="action-btn" @click="deleteTemplate(template)" title="Delete">
              <v-icon size="18" color="#ef4444">mdi-delete</v-icon>
            </button>
          </div>
        </div>

        <!-- Card Body -->
        <div class="card-body">
          <h3 class="template-name">{{ template.name }}</h3>
          <p v-if="template.description" class="template-description">{{ template.description }}</p>
          
          <!-- Metadata -->
          <div v-if="template.category || template.tags" class="template-meta">
            <span v-if="template.category" class="meta-badge">
              <v-icon size="12" left color="#14b8a6">mdi-folder</v-icon>
              {{ template.category }}
            </span>
            <span v-for="tag in template.tags" :key="tag" class="meta-badge meta-tag">
              {{ tag }}
            </span>
          </div>

          <!-- Stats -->
          <div class="template-stats">
            <div class="stat-item">
              <v-icon size="16" color="#64748b">mdi-clock-outline</v-icon>
              <span class="stat-text">{{ formatDate(template.created_at) }}</span>
            </div>
            <div v-if="template.usage_count" class="stat-item">
              <v-icon size="16" color="#64748b">mdi-file-check</v-icon>
              <span class="stat-text">{{ template.usage_count }} uses</span>
            </div>
          </div>
        </div>

        <!-- Card Footer -->
        <div class="card-footer">
          <button class="btn-use-template" @click="useTemplate(template)">
            <v-icon size="18" left color="white">mdi-check</v-icon>
            Use Template
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'TemplatesProfessional',
  data() {
    return {
      loading: false,
      searchQuery: '',
      templates: [
        {
          id: '1',
          name: 'Trade Finance Standard Response',
          description: 'Standard template for trade finance RFP responses covering LC, SBLC, and documentary collections',
          category: 'Trade Finance',
          tags: ['Letter of Credit', 'SBLC', 'Collections'],
          created_at: '2024-01-15',
          usage_count: 12
        },
        {
          id: '2',
          name: 'Payments & Cash Management',
          description: 'Comprehensive template for payment processing and cash management services',
          category: 'Payments',
          tags: ['ACH', 'Wire', 'Real-time Payments'],
          created_at: '2024-01-20',
          usage_count: 8
        },
        {
          id: '3',
          name: 'Treasury Services Overview',
          description: 'General treasury services template with liquidity management and reporting capabilities',
          category: 'Treasury',
          tags: ['Liquidity', 'Reporting', 'FX'],
          created_at: '2024-01-25',
          usage_count: 5
        }
      ],
      filteredTemplates: []
    }
  },
  mounted() {
    this.loadTemplates()
  },
  methods: {
    loadTemplates() {
      this.loading = true
      setTimeout(() => {
        this.filteredTemplates = [...this.templates]
        this.loading = false
      }, 500)
    },
    filterTemplates() {
      const query = this.searchQuery.toLowerCase()
      this.filteredTemplates = this.templates.filter(template => 
        template.name.toLowerCase().includes(query) ||
        template.description?.toLowerCase().includes(query) ||
        template.category?.toLowerCase().includes(query) ||
        template.tags?.some(tag => tag.toLowerCase().includes(query))
      )
    },
    createTemplate() {
      console.log('Create template clicked')
      // Navigate to template creation page or open modal
    },
    useTemplate(template) {
      console.log('Use template:', template.name)
      // Apply template logic
    },
    editTemplate(template) {
      console.log('Edit template:', template.name)
      // Navigate to edit page or open modal
    },
    deleteTemplate(template) {
      console.log('Delete template:', template.name)
      // Show confirmation dialog and delete
    },
    formatDate(dateStr) {
      if (!dateStr) return 'Unknown'
      const date = new Date(dateStr)
      return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
    }
  }
}
</script>

<style scoped>
/* === Color System === */
.templates-professional {
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

.templates-professional {
  padding: 0;
}

/* === Page Header === */
.page-header {
  padding: 32px 0 24px 0;
  border-bottom: 1px solid var(--slate-200);
  margin-bottom: 24px;
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

/* === Controls Bar === */
.controls-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
  margin-bottom: 32px;
}

.search-box {
  flex: 1;
  max-width: 400px;
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 16px;
  background-color: white;
  border: 1px solid var(--slate-300);
  border-radius: 8px;
  transition: all 0.2s ease;
}

.search-box:focus-within {
  border-color: var(--teal-500);
  box-shadow: 0 0 0 3px rgba(20, 184, 166, 0.1);
}

.search-input {
  flex: 1;
  border: none;
  outline: none;
  font-size: 14px;
  color: var(--slate-900);
  background: transparent;
}

.search-input::placeholder {
  color: var(--slate-400);
}

.btn-primary {
  background-color: var(--teal-500);
  color: white;
  border: none;
  border-radius: 6px;
  padding: 10px 20px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  gap: 6px;
  white-space: nowrap;
}

.btn-primary:hover {
  background-color: var(--teal-600);
}

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
  margin: 0 0 24px 0;
}

/* === Templates Grid === */
.templates-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 20px;
}

/* === Template Card === */
.template-card {
  background-color: white;
  border: 1px solid var(--slate-200);
  border-radius: 8px;
  overflow: hidden;
  transition: all 0.2s ease;
  display: flex;
  flex-direction: column;
}

.template-card:hover {
  border-color: var(--teal-500);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

/* === Card Header === */
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  background-color: var(--slate-50);
  border-bottom: 1px solid var(--slate-200);
}

.template-icon {
  width: 40px;
  height: 40px;
  background-color: var(--teal-50);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.card-actions {
  display: flex;
  gap: 8px;
}

.action-btn {
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
}

.action-btn:hover {
  background-color: var(--slate-100);
  border-color: var(--slate-300);
}

/* === Card Body === */
.card-body {
  padding: 20px;
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.template-name {
  font-size: 18px;
  font-weight: 600;
  color: var(--slate-900);
  margin: 0;
  line-height: 1.4;
}

.template-description {
  font-size: 14px;
  color: var(--slate-600);
  line-height: 1.5;
  margin: 0;
}

.template-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: auto;
}

.meta-badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  font-weight: 500;
  color: var(--teal-700);
  background-color: var(--teal-50);
  padding: 4px 10px;
  border-radius: 12px;
}

.meta-tag {
  color: var(--slate-700);
  background-color: var(--slate-100);
}

.template-stats {
  display: flex;
  gap: 16px;
  padding-top: 12px;
  border-top: 1px solid var(--slate-200);
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 6px;
}

.stat-text {
  font-size: 12px;
  color: var(--slate-600);
}

/* === Card Footer === */
.card-footer {
  padding: 16px 20px;
  border-top: 1px solid var(--slate-200);
}

.btn-use-template {
  width: 100%;
  background-color: var(--teal-500);
  color: white;
  border: none;
  border-radius: 6px;
  padding: 10px 20px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
}

.btn-use-template:hover {
  background-color: var(--teal-600);
}

/* === Responsive === */
@media (max-width: 768px) {
  .templates-grid {
    grid-template-columns: 1fr;
  }
  
  .controls-bar {
    flex-direction: column;
    align-items: stretch;
  }
  
  .search-box {
    max-width: none;
  }
  
  .btn-primary {
    width: 100%;
    justify-content: center;
  }
}
</style>
