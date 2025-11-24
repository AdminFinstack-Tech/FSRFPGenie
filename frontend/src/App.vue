<template>
  <v-app>
    <!-- Professional Minimal App Bar -->
    <v-app-bar
      app
      elevation="0"
      color="white"
      class="app-bar-professional"
      height="64"
    >
      <v-app-bar-nav-icon 
        @click="drawer = !drawer"
        color="slate-700"
      ></v-app-bar-nav-icon>
      
      <!-- Logo & Brand -->
      <v-toolbar-title class="brand-container">
        <div class="logo-text">
          FS RFP <span class="logo-accent">Genie</span>
        </div>
      </v-toolbar-title>

      <v-spacer></v-spacer>

      <!-- Primary Actions -->
      <v-btn 
        variant="flat"
        to="/upload"
        class="btn-primary mr-2"
        prepend-icon="mdi-cloud-upload"
      >
        Upload
      </v-btn>
      
      <v-btn 
        variant="outlined"
        to="/search"
        class="btn-secondary"
        prepend-icon="mdi-magnify"
      >
        Search
      </v-btn>
    </v-app-bar>

    <!-- Professional Side Navigation -->
    <v-navigation-drawer
      v-model="drawer"
      app
      color="white"
      class="nav-drawer-professional"
    >
      <v-list density="comfortable" class="nav-list">
        <v-list-item
          v-for="item in navItems"
          :key="item.title"
          :to="item.to"
          :prepend-icon="item.icon"
          class="nav-item"
          active-class="nav-item-active"
        >
          <v-list-item-title>{{ item.title }}</v-list-item-title>
        </v-list-item>
      </v-list>
    </v-navigation-drawer>

    <!-- Main Content -->
    <v-main class="main-content">
      <div class="content-wrapper">
        <router-view />
      </div>
    </v-main>
  </v-app>
</template>

<script>
export default {
  name: 'App',
  data() {
    return {
      drawer: true,
      navItems: [
        { title: 'Dashboard', icon: 'mdi-view-dashboard', to: '/' },
        { title: 'Upload Document', icon: 'mdi-cloud-upload', to: '/upload' },
        { title: 'Intelligent Search', icon: 'mdi-magnify', to: '/search' },
        { title: 'Documents', icon: 'mdi-file-document-multiple', to: '/documents' },
        { title: 'Templates', icon: 'mdi-text-box-multiple', to: '/templates' }
      ]
    }
  }
}
</script>

<style scoped>
/* === Professional Color System === */
:root {
  /* Slate (Neutral) */
  --slate-50:  #f8fafc;
  --slate-100: #f1f5f9;
  --slate-200: #e2e8f0;
  --slate-300: #cbd5e1;
  --slate-400: #94a3b8;
  --slate-500: #64748b;
  --slate-600: #475569;
  --slate-700: #334155;
  --slate-800: #1e293b;
  --slate-900: #0f172a;
  
  /* Teal (Accent) */
  --teal-50:  #f0fdfa;
  --teal-100: #ccfbf1;
  --teal-500: #14b8a6;
  --teal-600: #0d9488;
  --teal-700: #0f766e;
}

/* === App Bar === */
.app-bar-professional {
  border-bottom: 1px solid var(--slate-200) !important;
}

/* === Brand === */
.brand-container {
  margin-left: 8px;
}

.logo-text {
  font-size: 20px;
  font-weight: 700;
  color: var(--slate-900);
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}

.logo-accent {
  color: var(--teal-600);
}

/* === Buttons === */
.btn-primary {
  background-color: var(--teal-500) !important;
  color: white !important;
  text-transform: none !important;
  font-weight: 500 !important;
  letter-spacing: 0 !important;
  box-shadow: none !important;
}

.btn-primary:hover {
  background-color: var(--teal-600) !important;
}

.btn-secondary {
  background-color: white !important;
  color: var(--slate-700) !important;
  border: 1px solid var(--slate-300) !important;
  text-transform: none !important;
  font-weight: 500 !important;
  letter-spacing: 0 !important;
  box-shadow: none !important;
}

.btn-secondary:hover {
  background-color: var(--slate-50) !important;
  border-color: var(--slate-400) !important;
}

/* === Navigation Drawer === */
.nav-drawer-professional {
  border-right: 1px solid var(--slate-200) !important;
}

.nav-list {
  padding: 16px 8px !important;
}

.nav-item {
  border-radius: 6px !important;
  margin-bottom: 4px !important;
  color: var(--slate-600) !important;
}

.nav-item:hover {
  background-color: var(--slate-50) !important;
  color: var(--slate-900) !important;
}

.nav-item-active {
  background-color: var(--teal-50) !important;
  color: var(--teal-700) !important;
}

/* === Main Content === */
.main-content {
  background-color: var(--slate-50) !important;
}

.content-wrapper {
  padding: 24px;
  max-width: 1400px;
  margin: 0 auto;
}

/* === Global Overrides === */
:deep(.v-list-item-title) {
  font-weight: 500 !important;
}

:deep(.v-btn) {
  text-transform: none !important;
  letter-spacing: 0 !important;
}
</style>
