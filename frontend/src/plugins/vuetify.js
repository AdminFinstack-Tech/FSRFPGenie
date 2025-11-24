import '@mdi/font/css/materialdesignicons.css'
import 'vuetify/styles'
import { createVuetify } from 'vuetify'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'

const vuetify = createVuetify({
  components,
  directives,
  theme: {
    defaultTheme: 'light',
    themes: {
      light: {
        dark: false,
        colors: {
          primary: '#2B6CB0', // Indigo Blue (Finstack 2025)
          secondary: '#805AD5', // Purple Gradient
          accent: '#00B5D8', // Cyan
          teal: '#38B2AC', // Teal Accent
          error: '#EF4444',
          warning: '#F59E0B',
          info: '#00B5D8',
          success: '#10B981',
          background: '#F9FAFB', // Soft white
          surface: '#FFFFFF',
          textPrimary: '#2D3748', // Dark gray
          textSecondary: '#718096', // Muted tone
        }
      },
      dark: {
        dark: true,
        colors: {
          primary: '#4299E1', // Lighter blue for dark mode
          secondary: '#9F7AEA', // Lighter purple
          accent: '#00C4DB',
          teal: '#4FD1C5',
          error: '#F87171',
          warning: '#FBBF24',
          info: '#4299E1',
          success: '#34D399',
          background: '#1A202C',
          surface: '#2D3748',
          textPrimary: '#F7FAFC',
          textSecondary: '#A0AEC0',
        }
      }
    }
  },
  defaults: {
    VBtn: {
      rounded: 'md',
      flat: true,
      fontWeight: '500',
      letterSpacing: '0.025em'
    },
    VCard: {
      rounded: 'lg',
      elevation: 1
    },
    VTextField: {
      variant: 'outlined',
      density: 'comfortable',
      color: 'primary'
    },
    VSelect: {
      variant: 'outlined',
      density: 'comfortable',
      color: 'primary'
    }
  }
})

export default vuetify