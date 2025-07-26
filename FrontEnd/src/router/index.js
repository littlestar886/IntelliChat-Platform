import { createRouter, createWebHistory } from 'vue-router'
import WelcomePage from '../components/WelcomePage.vue'
import ChatPage from '../components/ChatPage.vue'
import HistoryPage from '../components/HistoryPage.vue'

const routes = [
  {
    path: '/',
    name: 'welcome',
    component: WelcomePage
  },
  {
    path: '/chat',
    name: 'chat',
    component: ChatPage
  },
  {
    path: '/history',
    name: 'history',
    component: HistoryPage
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router