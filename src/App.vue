<template>
  <div id="app-container">
    <!-- Общий хедер -->
    <header class="app-header">
      <div class="container header-container"> <!-- Добавим класс для возможной стилизации -->
        <span class="logo">Ломбард Авангард</span>
        <nav>
          <router-link to="/goods">Предметы залога</router-link>
          <router-link to="/profile">Личный кабинет</router-link>
          <router-link to="/booking">Корзина</router-link>
          <router-link to="/contacts">Контакты</router-link>
        </nav>
      </div>
    </header>

    <!-- Основной контент страницы будет здесь -->
    <router-view class="main-content"></router-view> 

    <!-- Общий футер -->
    <footer v-if="route.name !== 'Login' && route.name !== 'Register'" class="app-footer">
      <div class="container footer-content"> <!-- Добавим класс для возможной стилизации -->
        <div class="address">
          192019, Санкт-Петербург<br>
          Лермонтовский просп., 4, Санкт-Петербург
        </div>
        <div class="phone">
          +7 (812) 322-60-60
        </div>
      </div>
    </footer>
  </div>
</template>

<script setup>
// Импортируем useRoute для доступа к информации о текущем маршруте
import { useRoute } from 'vue-router';

// Получаем объект текущего маршрута
const route = useRoute();

// Логика App.vue (если нужна)
</script>

<style>
/* Глобальные стили (НЕ scoped) */

/* Стили для body и базовые настройки */
body {
  margin: 0;
  font-family: Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu,
    Cantarell, 'Fira Sans', 'Droid Sans', 'Helvetica Neue', sans-serif;
  background-color: #ffffff; 
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  display: flex; /* Используем flex для прижатия футера */
  flex-direction: column;
  min-height: 100vh;
}

#app-container {
  display: flex;
  flex-direction: column;
  flex-grow: 1; /* Позволяет контейнеру расти */
  /* Убираем padding отсюда, т.к. он мешал хедеру/футеру */
}

.container { /* Общий контейнер для ограничения ширины контента */
  width: 100%;
  max-width: 1140px; /* Стандартная ширина контента */
  margin: 0 auto;
  padding: 0 15px;
  box-sizing: border-box;
}

/* Основной контент страницы */
.main-content {
  flex-grow: 1; /* Занимает все доступное пространство между хедером и футером */
  /* Можно добавить вертикальные отступы здесь, если нужно */
   padding-top: 40px;
   padding-bottom: 140px; 
}

/* Стили для Хедера (переносим сюда) */
.app-header {
  background-color: #fff;
  border-bottom: 1px solid #e0e0e0;
  padding: 15px 0;
  width: 100%;
  flex-shrink: 0; /* Не сжиматься */
}

/* Используем общий .container для хедера */
.app-header .header-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.logo {
  font-size: 1.4rem;
  font-weight: 500;
  color: #333;
}

nav a {
  margin-left: 25px;
  text-decoration: none;
  color: #555;
  font-size: 0.95rem;
  transition: color 0.2s ease;
}

nav a:hover {
  color: #000;
}

/* Делаем ссылку Корзина черной (с !important) */
nav a[to="/booking"] {
  color: #000 !important;
}

/* Добавляем правило для АКТИВНОЙ ссылки Корзина */
nav a[to="/booking"].router-link-active, 
nav a[to="/booking"].router-link-exact-active { /* На всякий случай учтем оба класса */
  color: #000 !important; /* Гарантируем черный цвет */
}

/* Стили для Футера */
.app-footer {
  /* Возвращаем фон */
  background-color: #333;
  color: #ccc;
  /* Оставляем уменьшенные отступы */
  padding: 20px 0;
  width: 100%; 
  /* Оставляем уменьшенный шрифт */
  font-size: 0.8rem; 
  line-height: 1;
  position: fixed;
  bottom: 0;
  left: 0;
  z-index: 10; 
}

/* Используем общий .container для футера */
.app-footer .footer-content { 
    /* Убираем фон и отступы отсюда */
    /* background-color: #333; */
    /* padding: 30px 15px; */ 
    /* border-radius: 6px 6px 0 0; */ 

    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    flex-wrap: wrap; 
    gap: 20px;
}

.address {
    flex-basis: 60%;
    min-width: 250px;
}

.phone {
    flex-basis: 30%;
    min-width: 200px;
    text-align: right;
}

/* Глобальные стили для адаптивности хедера/футера */
@media (max-width: 768px) {
  .app-header .header-container {
    flex-direction: column;
    align-items: center;
    gap: 10px;
  }
  nav {
    text-align: center;
  }
  nav a {
    margin: 5px 10px;
    display: inline-block;
  }
  .app-footer .footer-content {
      flex-direction: column;
      align-items: center;
      text-align: center;
  }
  .phone {
      text-align: center;
      margin-top: 10px;
  }
}

/* (Удалены стили для #app из main.css, они теперь здесь или не нужны) */

</style>