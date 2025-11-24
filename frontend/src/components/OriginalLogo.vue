<template>
  <div class="original-logo-wrapper">
    <!-- Original Logo as SVG (scalable) -->
    <img 
      :src="logoSrc"
      :width="size"
      :height="size"
      alt="FS RFP Genie Logo"
      class="original-logo"
      :class="{ 'logo-animated': animated }"
      @error="handleLogoError"
    >
  </div>
</template>

<script>
export default {
  name: 'OriginalLogo',
  props: {
    size: {
      type: [Number, String],
      default: 48
    },
    animated: {
      type: Boolean,
      default: true
    }
  },
  data() {
    return {
      logoSrc: '/logo-original.svg', // SVG version (scalable)
      fallbackAttempted: false
    }
  },
  methods: {
    handleLogoError() {
      if (!this.fallbackAttempted) {
        console.warn('SVG logo failed, falling back to PNG')
        this.logoSrc = '/logo-old-backup.png'
        this.fallbackAttempted = true
      } else {
        console.error('Both SVG and PNG logos failed to load')
        this.$emit('logo-error')
      }
    }
  }
}
</script>

<style scoped>
.original-logo-wrapper {
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.original-logo {
  display: block;
  transition: all 0.3s ease;
  filter: drop-shadow(0 2px 8px rgba(255, 255, 255, 0.2));
}

.original-logo.logo-animated {
  animation: logoGlow 3s ease-in-out infinite;
}

@keyframes logoGlow {
  0%, 100% {
    filter: drop-shadow(0 2px 8px rgba(255, 255, 255, 0.2));
  }
  50% {
    filter: drop-shadow(0 4px 12px rgba(255, 255, 255, 0.4));
  }
}

.original-logo:hover {
  filter: drop-shadow(0 4px 16px rgba(56, 178, 172, 0.4));
  transform: scale(1.05);
}
</style>
