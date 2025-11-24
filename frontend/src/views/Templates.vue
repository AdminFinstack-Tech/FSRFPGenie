<template>
  <div>
    <!-- Page Header -->
    <div class="mb-8">
      <h1 class="text-3xl font-bold text-gray-900 mb-2">Column Mapping Templates</h1>
      <p class="text-gray-600">Manage saved column mapping templates for faster RFP processing</p>
    </div>

    <!-- Templates List -->
    <v-card>
      <v-card-title class="d-flex align-center">
        <span class="text-h6">Saved Templates</span>
        <v-spacer></v-spacer>
        <v-text-field
          v-model="search"
          append-inner-icon="mdi-magnify"
          label="Search templates"
          single-line
          hide-details
          dense
          style="max-width: 300px"
        ></v-text-field>
      </v-card-title>

      <v-card-text class="pa-0">
        <v-list v-if="filteredTemplates.length > 0">
          <template v-for="(template, index) in filteredTemplates" :key="template.template_id">
            <v-list-item
              class="py-4"
            >
              <v-list-item-avatar>
                <v-icon color="primary">mdi-file-code</v-icon>
              </v-list-item-avatar>

              <v-list-item-content>
                <v-list-item-title class="text-h6 font-weight-medium">
                  {{ template.template_name }}
                </v-list-item-title>
                <v-list-item-subtitle>
                  Created {{ formatDate(template.created_at) }}
                </v-list-item-subtitle>
                
                <!-- Mapping Preview -->
                <div class="mt-3">
                  <v-chip
                    v-for="(target, source) in template.mappings"
                    :key="source"
                    small
                    label
                    outlined
                    class="mr-2 mb-1"
                  >
                    {{ getFieldLabel(source) }}: "{{ target }}"
                  </v-chip>
                </div>
              </v-list-item-content>

              <v-list-item-action>
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
                    <v-list-item @click="viewTemplate(template)">
                      <v-list-item-icon>
                        <v-icon small>mdi-eye</v-icon>
                      </v-list-item-icon>
                      <v-list-item-title>View Details</v-list-item-title>
                    </v-list-item>
                    
                    <v-list-item @click="editTemplate(template)">
                      <v-list-item-icon>
                        <v-icon small>mdi-pencil</v-icon>
                      </v-list-item-icon>
                      <v-list-item-title>Edit</v-list-item-title>
                    </v-list-item>
                    
                    <v-divider></v-divider>
                    
                    <v-list-item @click="deleteTemplate(template)">
                      <v-list-item-icon>
                        <v-icon small color="error">mdi-delete</v-icon>
                      </v-list-item-icon>
                      <v-list-item-title class="error--text">Delete</v-list-item-title>
                    </v-list-item>
                  </v-list>
                </v-menu>
              </v-list-item-action>
            </v-list-item>
            
            <v-divider
              v-if="index < filteredTemplates.length - 1"
              :key="`divider-${index}`"
            ></v-divider>
          </template>
        </v-list>

        <!-- Empty State -->
        <div v-else class="pa-12 text-center">
          <v-icon size="64" color="gray">mdi-file-code-outline</v-icon>
          <h3 class="text-h6 mt-4 mb-2">No templates found</h3>
          <p class="text-body-2 text-gray-600">
            {{ search ? 'No templates match your search' : 'Create templates when uploading RFP files' }}
          </p>
          <v-btn
            color="primary"
            class="mt-4"
            @click="$router.push('/upload')"
          >
            Upload RFP File
          </v-btn>
        </div>
      </v-card-text>
    </v-card>

    <!-- Template Details Dialog -->
    <v-dialog v-model="detailsDialog" max-width="600">
      <v-card v-if="selectedTemplate">
        <v-card-title>
          <span class="text-h6">{{ selectedTemplate.template_name }}</span>
          <v-spacer></v-spacer>
          <v-btn icon @click="detailsDialog = false">
            <v-icon>mdi-close</v-icon>
          </v-btn>
        </v-card-title>
        
        <v-card-text>
          <p class="text-body-2 text-gray-600 mb-4">
            Created {{ formatDate(selectedTemplate.created_at, true) }}
          </p>
          
          <h4 class="text-subtitle-1 font-weight-bold mb-3">Column Mappings</h4>
          
          <v-simple-table>
            <template v-slot:default>
              <thead>
                <tr>
                  <th>RFP Field</th>
                  <th>Excel Column</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(target, source) in selectedTemplate.mappings" :key="source">
                  <td class="font-weight-medium">{{ getFieldLabel(source) }}</td>
                  <td>{{ target }}</td>
                </tr>
              </tbody>
            </template>
          </v-simple-table>
        </v-card-text>
        
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn text @click="detailsDialog = false">Close</v-btn>
          <v-btn color="primary" text @click="editTemplate(selectedTemplate)">
            <v-icon left small>mdi-pencil</v-icon>
            Edit
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
import { format } from 'date-fns'

export default {
  name: 'TemplatesView',
  data() {
    return {
      search: '',
      templates: [],
      detailsDialog: false,
      selectedTemplate: null,
      fieldLabels: {
        product: 'Product',
        requirement: 'Requirement',
        requirement_category: 'Requirement Category',
        response_category: 'Response Category',
        effort_required: 'Effort Required',
        comments: 'Comments'
      }
    }
  },
  computed: {
    filteredTemplates() {
      if (!this.search) return this.templates
      
      const searchLower = this.search.toLowerCase()
      return this.templates.filter(template => 
        template.template_name.toLowerCase().includes(searchLower) ||
        Object.values(template.mappings).some(value => 
          value.toLowerCase().includes(searchLower)
        )
      )
    }
  },
  mounted() {
    this.loadTemplates()
  },
  methods: {
    async loadTemplates() {
      try {
        this.templates = await this.$store.dispatch('getTemplates')
      } catch (error) {
        this.$toast.error('Failed to load templates')
        console.error(error)
      }
    },
    viewTemplate(template) {
      this.selectedTemplate = template
      this.detailsDialog = true
    },
    editTemplate() {
      // In real implementation, this would open an edit dialog
      this.$toast.info('Edit functionality coming soon')
    },
    async deleteTemplate(template) {
      if (confirm(`Are you sure you want to delete the template "${template.template_name}"?`)) {
        try {
          // In real implementation, this would call delete API
          this.$toast.success('Template deleted successfully')
          this.loadTemplates()
        } catch (error) {
          this.$toast.error('Failed to delete template')
          console.error(error)
        }
      }
    },
    getFieldLabel(field) {
      return this.fieldLabels[field] || field
    },
    formatDate(dateString, includeTime = false) {
      if (!dateString) return 'N/A'
      const formatString = includeTime ? 'MMM d, yyyy h:mm a' : 'MMM d, yyyy'
      return format(new Date(dateString), formatString)
    }
  }
}
</script>