<template>
  <div class="app-container">
    <!-- 加载动画 -->
    <div class="loader-wrapper" v-if="isLoading">
      <div class="loader">
        <div class="dot"></div>
        <div class="dot"></div>
        <div class="dot"></div>
      </div>
      <div class="loader-text">正在加载...</div>
    </div>

    <router-view v-slot="{ Component }">
      <transition name="fade" mode="out-in">
        <component :is="Component" />
      </transition>
    </router-view>
  </div>
</template>

<script>
import { ref } from 'vue'
import { useRoute } from 'vue-router'

export default {
  name: 'App',
  setup() {
    const isLoading = ref(false)
    const route = useRoute()

    // 模拟加载状态
    const checkLoading = () => {
      if (route.path === '/history') {
        isLoading.value = true
        setTimeout(() => {
          isLoading.value = false
        }, 500)
      }
    }

    return {
      isLoading,
      checkLoading
    }
  }
}
</script>

<style>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>