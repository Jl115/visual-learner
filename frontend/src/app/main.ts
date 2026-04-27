import { createApp } from 'vue'
import { createPinia } from 'pinia'
import router from './router'
import { ThemeProvider } from '@/shared/ui'
import App from './App.vue'
import '../style.css'
import './index.css'

const app = createApp(App)
app.use(createPinia())
app.use(router)
app.component('ThemeProvider', ThemeProvider)
app.mount('#app')
