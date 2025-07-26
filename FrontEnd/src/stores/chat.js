import { defineStore } from 'pinia'

export const useChatStore = defineStore('chat', {
  state: () => ({
    messages: [
      { type: 'ai', content: '您好！有什么可以帮您吗？' }
    ],
    history: []
  }),
  actions: {
    addMessage(content, type) {
      this.messages.push({ type, content })
    },
    clearChat() {
      this.messages = [{ type: 'ai', content: '您好！我是智能助手，请问有什么可以帮您吗？' }]
    },
    addToHistory(question, answer) {
      this.history.unshift({
        question,
        answer,
        timestamp: new Date().toLocaleString()
      })
    },
    clearHistory() {
      this.history = []
    },
    deleteHistoryItem(index) {
      this.history.splice(index, 1)
    }
  },
  persist: true // 如果需要本地存储可以添加插件
})