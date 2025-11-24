<template>
  <div class="finstack-logo-wrapper">
    <!-- SVG Logo (Primary) -->
    <svg 
      v-if="!usePngFallback"
      :width="size" 
      :height="size" 
      viewBox="0 0 48 48" 
      class="finstack-logo"
      :class="{ 'logo-animated': animated }"
      @error="handleSvgError"
    >
      <!-- Lamp with Stack/Grid motif -->
      <defs>
        <linearGradient :id="`logoGradient-${uniqueId}`" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" style="stop-color:#38B2AC;stop-opacity:1" />
          <stop offset="100%" style="stop-color:#805AD5;stop-opacity:1" />
        </linearGradient>
        <filter :id="`glow-${uniqueId}`">
          <feGaussianBlur stdDeviation="2" result="coloredBlur"/>
          <feMerge>
            <feMergeNode in="coloredBlur"/>
            <feMergeNode in="SourceGraphic"/>
          </feMerge>
        </filter>
      </defs>
      
      <!-- Base layers (stack motif) -->
      <rect 
        x="12" y="34" 
        width="24" height="3" 
        rx="1.5" 
        :fill="`url(#logoGradient-${uniqueId})`" 
        opacity="0.8"
      />
      <rect 
        x="14" y="30" 
        width="20" height="3" 
        rx="1.5" 
        :fill="`url(#logoGradient-${uniqueId})`" 
        opacity="0.9"
      />
      
      <!-- Lamp body -->
      <path 
        d="M 24 8 L 28 20 L 20 20 Z" 
        :fill="`url(#logoGradient-${uniqueId})`"
      />
      <rect 
        x="22" y="20" 
        width="4" height="8" 
        rx="1" 
        :fill="`url(#logoGradient-${uniqueId})`"
      />
      
      <!-- Light glow -->
      <circle 
        cx="24" cy="8" 
        r="4" 
        fill="#FFF" 
        opacity="0.3"
        :filter="animated ? `url(#glow-${uniqueId})` : ''"
      />
      
      <!-- Grid pattern -->
      <line 
        x1="18" y1="32" 
        x2="30" y2="32" 
        stroke="#FFF" 
        stroke-width="0.5" 
        opacity="0.4"
      />
      <line 
        x1="16" y1="36" 
        x2="32" y2="36" 
        stroke="#FFF" 
        stroke-width="0.5" 
        opacity="0.4"
      />
    </svg>

    <!-- PNG Fallback -->
    <img 
      v-else
      :src="pngSrc"
      :width="size"
      :height="size"
      alt="FS RFP Genie Logo"
      class="finstack-logo-png"
      @error="handlePngError"
    >
  </div>
</template>

<script>
export default {
  name: 'FinstackLogo',
  props: {
    size: {
      type: [Number, String],
      default: 48
    },
    animated: {
      type: Boolean,
      default: true
    },
    pngFallback: {
      type: Boolean,
      default: true
    }
  },
  data() {
    return {
      usePngFallback: false,
      uniqueId: Math.random().toString(36).substr(2, 9),
      pngSrc: '/logo-old-backup.png' // Original logo as fallback
    }
  },
  methods: {
    handleSvgError() {
      if (this.pngFallback) {
        console.warn('SVG logo failed to load, falling back to PNG')
        this.usePngFallback = true
      }
    },
    handlePngError() {
      console.error('Both SVG and PNG logos failed to load')
      // Could emit an event or show a text fallback
      this.$emit('logo-error')
    }
  }
}
</script>

<style scoped>
.finstack-logo-wrapper {
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.finstack-logo {
  filter: drop-shadow(0 2px 8px rgba(255, 255, 255, 0.2));
  transition: all 0.3s ease;
}

.finstack-logo.logo-animated {
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

.finstack-logo:hover {
  filter: drop-shadow(0 4px 16px rgba(56, 178, 172, 0.4));
  transform: scale(1.05);
}

.finstack-logo-png {
  display: block;
  filter: drop-shadow(0 2px 8px rgba(255, 255, 255, 0.2));
  transition: all 0.3s ease;
}

.finstack-logo-png:hover {
  filter: drop-shadow(0 4px 16px rgba(56, 178, 172, 0.4));
  transform: scale(1.05);
}
</style>
