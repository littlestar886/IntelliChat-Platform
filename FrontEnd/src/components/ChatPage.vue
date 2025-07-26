<template>
  <div class="chat-page">
    <div class="page-header">
      <button class="back-button" @click="goBack">&#8592;</button>
      <h2>智能对话平台</h2>
      <div class="action-buttons">
        <button class="action-btn" @click="clearChat"><i class="fas fa-trash"></i></button>
        <button class="action-btn" @click="exportChat"><i class="fas fa-download"></i></button>
      </div>
    </div>
    
    <div class="history-icon" @click="goToHistory">
      <div class="file-icon">
        <div class="file-top"></div>
        <div class="file-body"></div>
        <div class="file-pages"></div>
      </div>
      <span>历史记录</span>
    </div>
    
    <div class="chat-container">
      <div class="chat-messages" ref="chatMessages">
        <div 
          v-for="(message, index) in chatStore.messages" 
          :key="index" 
          class="message" 
          :class="message.type"
        >
          <div class="avatar">
            <i :class="message.type === 'ai' ? 'fas fa-robot' : 'fas fa-user'"></i>
          </div>
          <div class="content" :class="message.type === 'ai' ? 'ai-content' : 'user-content'">
            {{ message.content }}
          </div>
        </div>
      </div>
      <div class="chat-form">
        <div class="input-actions">
          <button class="upload-btn" @click="handleFileUpload"><i class="fas fa-paperclip"></i></button>
          <input 
            type="text" 
            v-model="question" 
            placeholder="请输入您的问题..." 
            @keypress.enter="submitQuestion"
          >
          <button 
            class="mic-btn" 
            :class="{ recording: isRecording }" 
            @click="toggleRecording"
          >
            <i class="fas" :class="isRecording ? 'fa-microphone-alt' : 'fa-microphone'"></i>
          </button>
        </div>
        <div class="send-container">
          <button class="send-btn" @click="submitQuestion">发送</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { useChatStore } from '../stores/chat'
import axios from 'axios'

export default {
  name: 'ChatPage',
  setup() {
    const router = useRouter()
    const chatStore = useChatStore()
    const question = ref('')
    const chatMessages = ref(null)
    const isRecording = ref(false)
    const recordingInterval = ref(null)
    const recordedText = ref('')
    
    const api = axios.create({
      baseURL: 'http://localhost:5000/api',
      withCredentials: true
    })

    const scrollToBottom = async () => {
      await nextTick()
      if (chatMessages.value) {
        chatMessages.value.scrollTop = chatMessages.value.scrollHeight
      }
    }

    const clearChat = () => {
      chatStore.clearChat()
      api.delete('/history')
        .then(() => console.log('历史记录已清空'))
        .catch(error => console.error('清空历史失败:', error))
    }

    const exportChat = () => {
      let chatText = '对话记录\n\n'
      chatStore.messages.forEach(message => {
        const type = message.type === 'ai' ? 'AI' : '用户'
        chatText += `${type}: ${message.content}\n`
      })
      
      const blob = new Blob([chatText], { type: 'text/plain' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = '对话记录.txt'
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      URL.revokeObjectURL(url)
    }

    const submitQuestion = async () => {
      const q = question.value.trim()
      if (!q) return
      
      chatStore.addMessage(q, 'user')
      question.value = ''
      await scrollToBottom()

      try {
        const response = await api.post('/chat', { message: q }, {
          headers: { 'Content-Type': 'application/json' }
        })
        chatStore.addMessage(response.data.response, 'ai')
      } catch (error) {
        const errorMsg = error.response?.data?.error || error.message
        chatStore.addMessage('请求失败: ' + errorMsg, 'ai')
      }
      await scrollToBottom()
    }

    const handleFileUpload = () => {
      const input = document.createElement('input')
      input.type = 'file'
      input.accept = 'image/*,.pdf,.doc,.docx'
      input.onchange = async (e) => {
        const file = e.target.files[0]
        if (!file) return
        
        chatStore.addMessage(`上传了文件：${file.name}`, 'user')
        await scrollToBottom()
        
        const formData = new FormData()
        formData.append('file', file)
        
        try {
          const response = await api.post('/upload', formData, {
            headers: { 'Content-Type': 'multipart/form-data' }
          })
          chatStore.addMessage(response.data.response, 'ai')
        } catch (error) {
          chatStore.addMessage('文件上传失败', 'ai')
        }
        await scrollToBottom()
      }
      input.click()
    }

    const toggleRecording = () => {
      isRecording.value = !isRecording.value
      
      if (isRecording.value) {
        recordedText.value = ''
        recordingInterval.value = setInterval(() => {
          recordedText.value += '...'
          if (recordedText.value.length > 10) {
            stopRecording()
            chatStore.addMessage('语音识别中...', 'ai')
            
            setTimeout(() => {
              chatStore.addMessage('您说：您好，我想了解人工智能的应用。', 'user')
            }, 1500)
          }
        }, 300)
      } else {
        stopRecording()
      }
    }

    const stopRecording = () => {
      clearInterval(recordingInterval.value)
    }

    const goBack = () => {
      router.push('/')
    }

    const goToHistory = () => {
      router.push('/history')
    }

    const loadHistory = async () => {
      try {
        const response = await api.get('/history')
        chatStore.clearChat()
        response.data.history.forEach(item => {
          chatStore.addMessage(item.content, item.type)
        })
        await scrollToBottom()
      } catch (error) {
        console.error('加载历史记录失败:', error)
      }
    }

    onMounted(() => {
      loadHistory()
    })

    return {
      question,
      chatMessages,
      isRecording,
      chatStore,
      clearChat,
      exportChat,
      submitQuestion,
      handleFileUpload,
      toggleRecording,
      goBack,
      goToHistory
    }
  }
}
</script>