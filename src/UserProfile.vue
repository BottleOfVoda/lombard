<template>
  <!-- Оставляем только main контент -->
  <main class="container content">
    <h1 class="page-title">Личный кабинет</h1>

    <!-- Сообщение об ошибке -->
    <div v-if="errorMessage" class="error-message">
      {{ errorMessage }}
    </div>

    <!-- Индикатор загрузки -->
    <div v-if="isLoading" class="loading-message">
      Загрузка данных...
    </div>

    <!-- Основной контент профиля (показывать только если нет загрузки и ошибок) -->
     <div v-if="!isLoading && !errorMessage && Object.keys(userData).length > 0" class="profile-content">
       <div class="user-data-section">
         <h2 class="section-title">Ваши данные</h2>
         <div class="user-data-block">
           <div class="data-item">
             <span class="data-label">Ваше ФИО:</span>
             <!-- Используем ?. для безопасного доступа, если данных нет -->
             <span class="data-value">{{ userData.full_name || 'Не указано' }}</span>
           </div>
           <div class="data-item">
             <span class="data-label">Ваш телефон:</span>
             <span class="data-value">{{ userData.phone_number || 'Не указано' }}</span>
           </div>
           <div class="data-item">
             <span class="data-label">Ваша эл. почта:</span>
             <span class="data-value">{{ userData.email || 'Не указано' }}</span>
           </div>
            <!-- Можно добавить и логин, если нужно -->
            <!-- <div class="data-item">
              <span class="data-label">Логин:</span>
              <span class="data-value">{{ userData.username }}</span>
            </div> -->
         </div>
       </div>
       <div class="image-section">
         <img src="https://avatars.mds.yandex.net/get-altay/1031166/2a0000018689c32e86885b804291594f707f/XXXL" alt="Pawn shop items" class="profile-image">
       </div>
     </div>
      <!-- Добавим сообщение, если данные не загружены, но ошибок нет -->
      <div v-else-if="!isLoading && !errorMessage" class="empty-message">
         Данные пользователя не загружены.
      </div>
  </main>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';
import config from './config';

const userData = ref({}); 
const isLoading = ref(false);
const errorMessage = ref(null);

const fetchUserData = async () => {
  isLoading.value = true;
  errorMessage.value = null;
  userData.value = {}; 

  const userId = localStorage.getItem('user_id');
  console.log("User ID from localStorage:", userId); // ЛОГ 1: Проверяем ID

  if (!userId) {
    errorMessage.value = "Ошибка: не удалось определить пользователя. Пожалуйста, войдите снова.";
    isLoading.value = false;
    return;
  }

  try {
    console.log(`Запрос данных для пользователя: /api/user/${userId}`); // ЛОГ 2: Проверяем URL запроса
    const response = await axios.get(`${config.API_URL}/api/user/${userId}`);
    console.log("Ответ от сервера:", response.data); // ЛОГ 3: Смотрим, что пришло
    userData.value = response.data;
    console.log("Данные записаны в userData:", userData.value); // ЛОГ 4: Проверяем присвоение
  } catch (error) {
    console.error("Ошибка при загрузке данных пользователя:", error); // ЛОГ 5: Смотрим ошибку
    // ... обработка ошибок ...
    if (error.response) {
        if (error.response.status === 404) {
            errorMessage.value = "Не удалось найти данные пользователя.";
        } else {
             errorMessage.value = `Ошибка сервера: ${error.response.data.message || error.response.status}`;
        }
    } else if (error.request) {
        errorMessage.value = "Не удалось подключиться к серверу для загрузки данных.";
    } else {
        errorMessage.value = "Произошла ошибка при запросе данных пользователя.";
    }
  } finally {
    isLoading.value = false;
  }
};

onMounted(() => {
  fetchUserData();
});

</script>

<style scoped>
/* Стили, специфичные для UserProfile.vue */
.container { 
  /* Если нужно, чтобы контейнер здесь имел ограничение */
  /* max-width: 1140px; */ 
  /* margin: 0 auto; */
}

.content {
 /* Если отступы не заданы в App.vue .main-content, можно добавить здесь */
}

.page-title {
  text-align: center;
  font-size: 2rem;
  font-weight: 500;
  margin-bottom: 40px;
  color: #333;
}

.profile-content {
  display: flex;
  flex-wrap: wrap;
  gap: 40px;
  align-items: flex-start;
}

.user-data-section {
  flex: 1;
  min-width: 300px;
}

.image-section {
  flex: 1;
  min-width: 300px;
  text-align: center;
}

.section-title {
  font-size: 1.5rem;
  font-weight: 500;
  margin-bottom: 25px;
  color: #333;
}

.user-data-block {
  background-color: #f9f9f9;
  padding: 25px;
  border-radius: 8px;
  border: 1px solid #eee;
}

.data-item {
  margin-bottom: 18px;
  display: flex;
  align-items: baseline;
}

.data-item:last-child {
  margin-bottom: 0;
}

.data-label {
  font-weight: bold;
  color: #333;
  min-width: 150px;
  padding-right: 10px;
}

.data-value {
  color: #333; /* <<< Устанавливаем черный цвет */
}

.profile-image {
  max-width: 100%;
  height: auto;
  border-radius: 8px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}

/* Стили для сообщений */
.error-message {
  color: red;
  text-align: center;
  padding: 20px;
  font-weight: bold;
}

.loading-message {
  text-align: center;
  padding: 40px;
  font-size: 1.2rem;
  color: #555;
}

.empty-message { 
  text-align: center;
  padding: 40px;
  font-size: 1.1rem;
  color: #777;
}

/* Адаптивные стили */
@media (max-width: 768px) {
  .page-title {
    font-size: 1.8rem;
  }
  .profile-content {
    flex-direction: column;
    align-items: center;
  }
  .user-data-section, .image-section {
    width: 100%;
    max-width: 500px;
  }
}
</style> 