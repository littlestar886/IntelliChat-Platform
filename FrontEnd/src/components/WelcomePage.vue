<template>
    <div class="welcome-page">
      <div class="welcome-header">
        <h1>对话平台</h1>
        <p>人工智能交互系统</p>
      </div>
      <div class="team-info">
        <p>大创小组</p>
        <p>负责人：朱明楠 | 成员：赵锦川、郭苍菊、陈逸风、许昊林</p>
      </div>
      <div class="enter-section">
        <button class="enter-btn" @click="navigateToChat">开始对话</button>
      </div>
      <div class="features">
        <div class="feature-item">
          <i class="fas fa-comments"></i>
          <p>智能对话</p>
        </div>
        <div class="feature-item">
          <i class="fas fa-history"></i>
          <p>对话记录</p>
        </div>
        <div class="feature-item">
          <i class="fas fa-file-alt"></i>
          <p>文件分析</p>
        </div>
      </div>
    </div>
  </template>
  
  <script>
  import { onMounted } from 'vue'
  import { useRouter } from 'vue-router'
  
  export default {
    name: 'WelcomePage',
    setup() {
      const router = useRouter()
  
      onMounted(() => {
        // 动画效果
        setTimeout(() => {
          document.querySelector('.welcome-header').style.opacity = 1
          document.querySelector('.welcome-header').style.transform = 'translateY(0)'
        }, 300)
        
        setTimeout(() => {
          document.querySelector('.team-info').style.opacity = 1
          document.querySelector('.team-info').style.transform = 'translateY(0)'
        }, 600)
        
        setTimeout(() => {
          document.querySelector('.enter-section').style.opacity = 1
          document.querySelector('.enter-section').style.transform = 'translateY(0)'
        }, 900)
        
        setTimeout(() => {
          document.querySelector('.features').style.opacity = 1
          document.querySelector('.features').style.transform = 'translateY(0)'
        }, 1200)
      })
  
      const navigateToChat = () => {
        router.push('/chat')
      }
  
      return {
        navigateToChat
      }
    }
  }
  </script>