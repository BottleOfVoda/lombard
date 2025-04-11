import './assets/main.css' // Если у вас есть базовые стили

import { createApp } from 'vue'
import App from './App.vue'
import router from './router' // Импортируем настроенный роутер

const app = createApp(App)

app.use(router) // Подключаем роутер к приложению

app.mount('#app')