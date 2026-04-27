import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from '../App.vue'
import '../style.css'   // DESIGN.md token variables (must load before Tailwind)
import './index.css'

const app = createApp(App)
app.use(createPinia())
app.mount('#app')
