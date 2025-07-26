<template>
    <div class="history-page">
      <div class="page-header">
        <button class="back-button" @click="goBack">&#8592;</button>
        <h2>对话历史</h2>
        <div class="action-buttons">
          <button class="action-btn" @click="clearHistory"><i class="fas fa-trash"></i></button>
        </div>
      </div>
      
      <div class="history-list">
        <div v-if="history.length === 0" class="history-item placeholder">
          <i class="fas fa-comment-slash"></i>
          <p>暂无历史记录</p>
        </div>
        
        <div 
          v-for="(item, index) in history" 
          :key="index" 
          class="history-item"
        >
          <div class="history-header">
            <span>{{ item.timestamp }}</span>
            <i class="fas fa-trash" @click="deleteHistoryItem(index)"></i>
          </div>
          <div class="question">Q: {{ item.question }}</div>
          <div class="answer">A: {{ item.answer }}</div>
        </div>
      </div>
    </div>
  </template>
  
  <script>
  import { useRouter } from 'vue-router'
  import { useChatStore } from '../stores/chat'
  
  export default {
    name: 'HistoryPage',
    setup() {
      const router = useRouter()
      const chatStore = useChatStore()
      
      const { history } = chatStore
  
      const clearHistory = () => {
        chatStore.clearHistory()
      }
  
      const deleteHistoryItem = (index) => {
        chatStore.deleteHistoryItem(index)
      }
  
      const goBack = () => {
        router.push('/chat')
      }
  
      return {
        history,
        clearHistory,
        deleteHistoryItem,
        goBack
      }
    }
  }
  </script>