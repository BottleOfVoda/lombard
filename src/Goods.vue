<template>
  <main class="container content">
    <h1 class="page-title">Предметы залога</h1>

    <!-- Сообщение об ошибке -->
    <div v-if="errorMessage" class="error-message">{{ errorMessage }}</div>

    <!-- Индикатор загрузки -->
    <div v-if="isLoading" class="loading-message">Загрузка товаров...</div>

    <!-- Блок управления: Админка, Сортировка, Поиск -->
    <div class="controls-block">
      <!-- Кнопка "Добавить товар" (только для админа) -->
      <div class="add-item-controls" v-if="userRole === 'admin'">
        <button @click="showAddItemForm = !showAddItemForm" class="add-toggle-button">
          {{ showAddItemForm ? 'Скрыть форму добавления' : 'Добавить новый товар' }}
        </button>
      </div>

      <!-- Форма добавления товара -->
      <div v-if="showAddItemForm && userRole === 'admin'" class="add-item-form">
        <h3 class="form-title">Добавление нового товара</h3>
        <form @submit.prevent="addItem">
          <div class="form-group">
            <label for="itemName">Название:</label>
            <input type="text" id="itemName" v-model="newItemName" required>
          </div>
          <div class="form-group">
            <label for="itemPrice">Цена:</label>
            <input type="number" id="itemPrice" v-model="newItemPrice" step="0.01" required>
          </div>
          <div class="form-group">
            <label for="itemImageUrl">URL изображения (необязательно):</label>
            <input type="url" id="itemImageUrl" v-model="newItemImageUrl">
          </div>
          <button type="submit" class="add-item-button">Добавить товар</button>
        </form>
      </div>

      <!-- Фильтры и Сортировка -->
      <div v-if="!isLoading && !errorMessage && items.length > 0" class="filter-sort-controls">
        <!-- Поле поиска -->
        <div class="search-control">
          <input type="search" v-model.trim="searchQuery" placeholder="Поиск по названию...">
        </div>
        <!-- Сортировка -->
        <div class="sort-control">
          <label for="sort-select">Сортировать: </label>
          <select id="sort-select" v-model="sortOption">
            <option value="default">По умолчанию</option>
            <option value="name_asc">По названию (А-Я)</option>
            <option value="price_asc">По цене (сначала дешевые)</option>
            <option value="price_desc">По цене (сначала дорогие)</option>
          </select>
        </div>
      </div>
    </div>

    <!-- Сетка товаров -->
    <div v-if="!isLoading && !errorMessage" class="product-grid">
      <!-- Отображаем отфильтрованные и отсортированные товары -->
      <div v-if="filteredAndSortedItems.length > 0" class="product-card" v-for="item in filteredAndSortedItems" :key="item.id">
        <!-- Используем item.image_url -->
        <img :src="item.image_url || 'https://via.placeholder.com/200x150.png/eee/aaa?text=No+Image'" :alt="item.name" class="product-image">
        <h3 class="product-name">{{ item.name }}</h3>
        <!-- Используем item.price -->
        <p class="product-price">Цена: {{ item.price }}р</p>
        
        <!-- Кнопки действий (бронь/разбронь и удаление) -->
        <div class="product-actions">
          <!-- Кнопка удаления (только для админа) -->
          <button 
            v-if="userRole === 'admin'" 
            @click="deleteItem(item)" 
            class="delete-button" 
            title="Удалить товар"
            :disabled="bookingState[item.id] === 'deleting'"> 
            <span v-if="bookingState[item.id] === 'deleting'">⏳</span>
            <svg v-else xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-trash3" viewBox="0 0 16 16">
              <path d="M6.5 1h3a.5.5 0 0 1 .5.5v1H6v-1a.5.5 0 0 1 .5-.5ZM11 2.5v-1A1.5 1.5 0 0 0 9.5 0h-3A1.5 1.5 0 0 0 5 1.5v1H2.506a.58.58 0 0 0-.01 0H1.5a.5.5 0 0 0 0 1h.538l.853 10.66A2 2 0 0 0 4.885 16h6.23a2 2 0 0 0 1.994-1.84l.853-10.66h.538a.5.5 0 0 0 0-1h-.995a.59.59 0 0 0-.01 0H11Zm1.958 1-.846 10.58a1 1 0 0 1-.997.92h-6.23a1 1 0 0 1-.997-.92L3.042 3.5h9.916Zm-7.487 1a.5.5 0 0 1 .528.47l.5 8.5a.5.5 0 0 1-.998.06L5 5.03a.5.5 0 0 1 .47-.53Zm5.058 0a.5.5 0 0 1 .47.53l-.5 8.5a.5.5 0 1 1-.998-.06l.5-8.5a.5.5 0 0 1 .528-.47ZM8 4.5a.5.5 0 0 1 .5.5v8.5a.5.5 0 0 1-1 0V5a.5.5 0 0 1 .5-.5Z"/>
            </svg>
          </button>

          <!-- Кнопка или галочка бронирования (НЕ для админа или если админ - не показывать одновременно с удалением?) -->
          <!-- Решаем: показывать бронь админу или нет? Пока оставлю как было -->
          <button 
            v-if="!item.is_booked" 
            class="add-button" 
            title="Забронировать" 
            @click="bookItem(item)" 
            :disabled="bookingState[item.id] === 'loading' || bookingState[item.id] === 'deleting'" >
            <!-- Показываем спиннер во время загрузки бронирования -->
            <span v-if="bookingState[item.id] === 'loading'">⏳</span>
            <!-- Показываем иконку ошибки, если была ошибка -->
            <span v-else-if="bookingState[item.id] === 'error'">⚠️</span>
            <!-- Иначе показываем плюс -->
            <svg v-else xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-plus-circle" viewBox="0 0 16 16">
              <path d="M8 15A7 7 0 1 1 8 1a7 7 0 0 1 0 14zm0 1A8 8 0 1 0 8 0a8 8 0 0 0 0 16z"/>
              <path d="M8 4a.5.5 0 0 1 .5.5v3h3a.5.5 0 0 1 0 1h-3v3a.5.5 0 0 1-1 0v-3h-3a.5.5 0 0 1 0-1h3v-3A.5.5 0 0 1 8 4z"/>
            </svg>
          </button>
          <div 
            v-else 
            class="booked-indicator" 
            title="Снять бронь" 
            @click="!(bookingState[item.id] === 'deleting') && unbookItem(item)" 
            :style="{ 
              cursor: bookingState[item.id] === 'loading' || bookingState[item.id] === 'deleting' ? 'wait' : 'pointer',
              opacity: bookingState[item.id] === 'deleting' ? 0.5 : 1
            }" >
            <!-- Показываем спиннер во время загрузки снятия брони -->
            <span v-if="bookingState[item.id] === 'loading'">⏳</span> 
            <!-- Показываем иконку ошибки, если была ошибка -->
            <span v-else-if="bookingState[item.id] === 'error'">⚠️</span>
            <!-- Иначе показываем галочку -->
            <svg v-else xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="green" class="bi bi-check-circle-fill" viewBox="0 0 16 16">
              <path d="M16 8A8 8 0 1 1 0 8a8 8 0 0 1 16 0zm-3.97-3.03a.75.75 0 0 0-1.08.022L7.477 9.417 5.384 7.323a.75.75 0 0 0-1.06 1.06L6.97 11.03a.75.75 0 0 0 1.079-.02l3.992-4.99a.75.75 0 0 0-.01-1.05z"/>
            </svg>
          </div>
        </div>
      </div>
       <!-- Сообщение, если после фильтрации/поиска товаров не найдено -->
      <div v-else-if="searchQuery && filteredAndSortedItems.length === 0" class="empty-message">
        По вашему запросу "{{ searchQuery }}" ничего не найдено.
      </div>
       <!-- Сообщение, если товаров нет изначально -->
      <div v-else-if="!items.length" class="empty-message">
        Нет доступных товаров.
      </div>
    </div>
  </main>
</template>

<script setup>
// Импортируем ref и onMounted из Vue, и axios для HTTP-запросов
import { ref, onMounted, computed } from 'vue';
import axios from 'axios';
import config from './config';

// Состояние для хранения списка товаров
const items = ref([]); 
// Состояние для отслеживания загрузки
const isLoading = ref(false);
// Состояние для хранения сообщения об ошибке
const errorMessage = ref(null);
// Добавляем состояние для отслеживания процесса бронирования для конкретного товара
const bookingState = ref({}); // { itemId: 'loading' | 'error', ... }

// Ref для хранения выбранной сортировки
const sortOption = ref('default');
// Ref для поиска
const searchQuery = ref('');

// --- Логика админки ---
const userRole = ref(null);
const newItemName = ref('');
const newItemPrice = ref('');
const newItemImageUrl = ref('');
const showAddItemForm = ref(false);

const addItem = async () => {
  if (!newItemName.value || newItemPrice.value === null) {
    errorMessage.value = "Название и цена обязательны.";
    return;
  }
  isLoading.value = true;
  errorMessage.value = null;

  try {
    await axios.post(`${config.API_URL}/api/products`, {
      name: newItemName.value,
      price: newItemPrice.value,
      image_url: newItemImageUrl.value
    });
    // Очистить форму
    newItemName.value = '';
    newItemPrice.value = null;
    newItemImageUrl.value = '';
    // Обновить список товаров
    await fetchItems(); 
  } catch (error) {
    console.error("Ошибка при добавлении товара:", error);
    if (error.response) {
        errorMessage.value = `Ошибка сервера: ${error.response.data.message || error.response.status}`;
    } else if (error.request) {
        errorMessage.value = "Не удалось подключиться к серверу.";
    } else {
        errorMessage.value = "Произошла ошибка при добавлении товара.";
    }
  } finally {
    isLoading.value = false;
  }
};

// Вычисляемое свойство для фильтрации и сортировки товаров
const filteredAndSortedItems = computed(() => {
  let itemsToDisplay = [...items.value]; // Копируем массив для обработки

  // 1. Фильтрация по поисковому запросу (если он есть)
  if (searchQuery.value) {
    const lowerCaseQuery = searchQuery.value.toLowerCase();
    itemsToDisplay = itemsToDisplay.filter(item =>
      item.name && item.name.toLowerCase().includes(lowerCaseQuery) // Проверяем наличие item.name
    );
  }

  // 2. Сортировка отфильтрованного массива
  switch (sortOption.value) {
    case 'name_asc':
      itemsToDisplay.sort((a, b) => (a.name || '').localeCompare(b.name || '')); // Учитываем возможное отсутствие name
      break;
    case 'price_asc':
      itemsToDisplay.sort((a, b) => Number(a.price || 0) - Number(b.price || 0)); // Учитываем возможное отсутствие price
      break;
    case 'price_desc':
      itemsToDisplay.sort((a, b) => Number(b.price || 0) - Number(a.price || 0)); // Учитываем возможное отсутствие price
      break;
    // 'default': оставляем порядок после фильтрации (или исходный, если фильтра не было)
  }

  return itemsToDisplay;
});

// Асинхронная функция для загрузки товаров с бэкенда
const fetchItems = async () => {
  isLoading.value = true;    // Начинаем загрузку
  errorMessage.value = null; // Сбрасываем предыдущие ошибки
  try {
    // Делаем GET-запрос к нашему API
    const response = await axios.get(`${config.API_URL}/api/products`);
    // Записываем полученные данные в items
    items.value = response.data;
  } catch (error) {
    console.error("Ошибка при загрузке товаров:", error);
    if (error.response) {
        errorMessage.value = `Ошибка сервера: ${error.response.data.message || error.response.status}`;
    } else if (error.request) {
        errorMessage.value = "Не удалось подключиться к серверу для загрузки товаров.";
    } else {
        errorMessage.value = "Произошла ошибка при запросе товаров.";
    }
  } finally {
    isLoading.value = false; // Заканчиваем загрузку (в любом случае)
  }
};

// --- Метод для бронирования товара ---
const bookItem = async (item) => {
  // Проверяем, не идет ли уже бронирование этого товара
  if (bookingState.value[item.id] === 'loading') {
    return;
  }
  
  // Устанавливаем состояние загрузки для этого товара
  bookingState.value = { ...bookingState.value, [item.id]: 'loading' };
  let bookingError = null; // Локальная ошибка для алерта

  try {
    // Отправляем PUT-запрос на бэкенд
    await axios.put(`${config.API_URL}/api/products/${item.id}/book`);


    const index = items.value.findIndex(i => i.id === item.id);
    if (index !== -1) {
      items.value[index].is_booked = true;
    }
    // Убираем состояние загрузки/ошибки для этого товара
    const newBookingState = { ...bookingState.value };
    delete newBookingState[item.id];
    bookingState.value = newBookingState;


  } catch (error) {
    console.error(`Ошибка при бронировании товара ${item.id}:`, error);
     if (error.response) {
        bookingError = `Ошибка сервера: ${error.response.data.message || error.response.status}`;
    } else if (error.request) {
        bookingError = "Не удалось подключиться к серверу для бронирования.";
    } else {
        bookingError = "Произошла ошибка при запросе бронирования.";
    }
    // Устанавливаем состояние ошибки для этого товара
    bookingState.value = { ...bookingState.value, [item.id]: 'error' };
    alert(bookingError);

  }
};

// --- Метод для СНЯТИЯ брони товара ---
const unbookItem = async (item) => {
  // Проверяем, не идет ли уже операция с этим товаром
  if (bookingState.value[item.id] === 'loading') {
    return;
  }
  
  // Устанавливаем состояние загрузки для этого товара
  bookingState.value = { ...bookingState.value, [item.id]: 'loading' };
  let bookingError = null; 

  try {
    // Отправляем PUT-запрос на бэкенд
    await axios.put(`${config.API_URL}/api/products/${item.id}/unbook`);

    // Если запрос успешен, обновляем состояние товара ЛОКАЛЬНО
    const index = items.value.findIndex(i => i.id === item.id);
    if (index !== -1) {
      items.value[index].is_booked = false;
    }
    // Убираем состояние загрузки/ошибки для этого товара
    const newBookingState = { ...bookingState.value };
    delete newBookingState[item.id];
    bookingState.value = newBookingState;
    
    // alert(`Бронь с товара "${item.name}" снята!`); // Опционально

  } catch (error) {
    console.error(`Ошибка при снятии брони с товара ${item.id}:`, error);
     if (error.response) {
        bookingError = `Ошибка сервера: ${error.response.data.message || error.response.status}`;
    } else if (error.request) {
        bookingError = "Не удалось подключиться к серверу для снятия брони.";
    } else {
        bookingError = "Произошла ошибка при запросе снятия брони.";
    }
    // Устанавливаем состояние ошибки для этого товара
    bookingState.value = { ...bookingState.value, [item.id]: 'error' };
    // Показываем ошибку пользователю
    alert(bookingError);
    // Опционально сбрасываем состояние ошибки через время
    // setTimeout(() => { ... });
  }
};

// --- Метод для удаления товара --- 
const deleteItem = async (item) => {
  // Проверяем, не идет ли уже операция с этим товаром
  if (bookingState.value[item.id] === 'loading' || bookingState.value[item.id] === 'deleting') {
    return;
  }

  // Запрашиваем подтверждение
  if (!window.confirm(`Вы уверены, что хотите удалить товар "${item.name}"?`)) {
    return;
  }

  // Устанавливаем состояние загрузки для этого товара
  bookingState.value = { ...bookingState.value, [item.id]: 'deleting' }; 
  errorMessage.value = null; // Сбрасываем общую ошибку

  try {
    // Отправляем DELETE-запрос на бэкенд
    await axios.delete(`${config.API_URL}/api/products/${item.id}`);
    
    // Если запрос успешен, удаляем товар из ЛОКАЛЬНОГО списка
    items.value = items.value.filter(i => i.id !== item.id);

    // Убираем состояние загрузки/ошибки для этого товара
    const newBookingState = { ...bookingState.value };
    delete newBookingState[item.id];
    bookingState.value = newBookingState;

  } catch (error) {
    console.error(`Ошибка при удалении товара ${item.id}:`, error);
    let deleteErrorMsg = "Произошла ошибка при удалении товара.";
    if (error.response) {
      deleteErrorMsg = `Ошибка сервера: ${error.response.data.message || error.response.status}`;
    } else if (error.request) {
      deleteErrorMsg = "Не удалось подключиться к серверу для удаления.";
    }
    // Устанавливаем состояние ошибки (можно использовать тот же 'error', если хотим универсальный значок)
    bookingState.value = { ...bookingState.value, [item.id]: 'error' }; 
    // Показываем ошибку пользователю (можно использовать errorMessage или alert)
    errorMessage.value = deleteErrorMsg; // Показываем ошибку в общем блоке
    // alert(deleteErrorMsg); // Или через alert
  }
};

// Вызываем функцию загрузки товаров при монтировании компонента
onMounted(() => {
  // Получаем роль пользователя при монтировании
  userRole.value = localStorage.getItem('user_role');
  // Логируем прочитанное значение
  console.log('User Role from localStorage on mount:', userRole.value);
  fetchItems();
});
</script>

<style scoped>
/* УДАЛЯЕМ СТИЛИ ДЛЯ .goods-page, .app-header, .logo, nav a, .app-footer, .footer-content, .address, .phone */
/* УДАЛЯЕМ ИЛИ ОСТАВЛЯЕМ .container В ЗАВИСИМОСТИ ОТ ТОГО, НУЖНО ЛИ ОГРАНИЧИВАТЬ ШИРИНУ КОНТЕНТА */
.container { /* Если контент должен быть ограничен по ширине */
   /* Если не нужно, можно убрать */
   /* Если нужно, чтобы он наследовал max-width из App.vue, 
      то этот класс можно вообще убрать из <main> и стилей здесь 
      (при условии, что .main-content в App.vue имеет padding) */
}

/* Оставляем стили для .content (если он используется) */
.content {
 /* Если отступы заданы в .main-content в App.vue, эти можно убрать */
 /* padding-top: 40px; */
 /* padding-bottom: 60px; */
}

/* Оставляем стили, специфичные для Goods.vue */
.page-title {
  text-align: center;
  font-size: 2rem;
  font-weight: 500;
  margin-bottom: 40px;
  color: #333;
}

.product-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 30px;
}

.product-card {
  background-color: #fff;
  border: 1px solid #f0f0f0;
  border-radius: 8px;
  padding: 20px;
  text-align: center;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  transition: box-shadow 0.3s ease;
  position: relative;
}

.product-card:hover {
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}

.product-image {
  max-width: 100%;
  height: 150px;
  object-fit: contain;
  margin-bottom: 15px;
}

.product-name {
  font-size: 1.1rem;
  font-weight: 500;
  margin-bottom: 8px;
  color: #333;
}

.product-price {
  font-size: 1rem;
  color: #666;
  margin-bottom: 15px;
}

.add-button {
  background: none;
  border: none;
  padding: 5px;
  cursor: pointer;
  position: absolute;
  bottom: 15px;
  right: 15px;
  color: #555;
  transition: color 0.2s ease;
}

.add-button:hover {
  color: #000;
}

.add-button svg {
  width: 24px;
  height: 24px;
}

.booked-indicator {
  position: absolute;
  bottom: 15px;
  right: 15px;
  padding: 5px;
}

.booked-indicator svg {
  width: 24px;
  height: 24px;
}

.error-message { /* Стили сообщений */
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
  grid-column: 1 / -1;
}

.add-button:disabled {
  cursor: not-allowed;
  opacity: 0.6;
}

/* Адаптивные стили только для контента Goods.vue */
@media (max-width: 768px) {
  .page-title {
    font-size: 1.8rem;
  }
  .product-grid {
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 20px;
  }
}

@media (max-width: 480px) {
    .product-grid {
        grid-template-columns: 1fr; /* Single column on very small screens */
    }
}

@media (min-width: 1024px) {
  .product-grid {
    grid-template-columns: repeat(4, 1fr); /* 4 колонки */
  }
}

/* Стили для блока управления над сеткой */
.controls-block {
  margin-bottom: 30px;
}

/* Контейнер для фильтра и сортировки */
.filter-sort-controls {
  display: flex;
  justify-content: space-between; /* Разносим поиск и сортировку */
  align-items: center;
  flex-wrap: wrap; /* Перенос на новую строку на мал. экранах */
  gap: 20px; /* Отступ между элементами */
  margin-top: 20px; /* Отступ от формы добавления (если она есть) */
  padding: 15px;
  background-color: #f8f9fa;
  border-radius: 6px;
}

.search-control input[type="search"] {
  padding: 8px 12px;
  border: 1px solid #ced4da;
  border-radius: 4px;
  min-width: 250px; /* Минимальная ширина поля поиска */
}

.sort-control label {
  margin-right: 8px;
  color: #000; /* Черный цвет для надписи "Сортировать:" */
}

.sort-control select {
  padding: 8px 10px;
  border: 1px solid #ced4da;
  border-radius: 4px;
}

/* Стили для контейнера кнопок действий */
.product-actions {
  position: absolute;
  bottom: 15px;
  right: 15px;
  display: flex; /* Располагаем кнопки в ряд */
  gap: 8px; /* Пространство между кнопками */
}

/* Убираем абсолютное позиционирование у отдельных кнопок */
.add-button,
.booked-indicator,
.delete-button {
  position: static; /* Убираем position: absolute */
  padding: 0; /* Убираем лишние паддинги, если есть */
  display: flex; /* Для центрирования контента внутри кнопки/индикатора */
  align-items: center;
  justify-content: center;
  width: 28px; /* Фиксированная ширина для выравнивания */
  height: 28px; /* Фиксированная высота */
  border-radius: 50%; /* Делаем круглыми */
  cursor: pointer;
  transition: background-color 0.2s ease, opacity 0.2s ease;
}

/* Стили кнопки бронирования (плюс) */
.add-button {
  background-color: #e9ecef;
  color: #495057;
  border: none;
}
.add-button:hover {
  background-color: #ced4da;
}
.add-button:disabled {
  background-color: #e9ecef;
  opacity: 0.6;
  cursor: not-allowed;
}
.add-button svg {
  width: 16px;
  height: 16px;
}

/* Стили индикатора брони (галочка) */
.booked-indicator {
  /* Можно добавить фон, если нужно */
}
.booked-indicator svg {
  width: 24px;
  height: 24px;
}

/* Стили для кнопки удаления (корзина) */
.delete-button {
  background-color: #f8d7da; /* Светло-красный фон */
  color: #721c24; /* Темно-красный цвет иконки */
  border: none;
  /* font-size: 16px; */ /* Убираем font-size, размер задается SVG */
}

.delete-button:hover {
  background-color: #f5c6cb;
}

.delete-button:disabled {
  background-color: #f8d7da;
  opacity: 0.6;
  cursor: not-allowed;
}

/* Стили для формы добавления товара */
.add-item-form {
  margin-bottom: 30px;
  padding: 25px;
  background: linear-gradient(to right, #f9f9ff, #f0f8ff);
  border-radius: 10px;
  box-shadow: 0 3px 10px rgba(0, 0, 0, 0.08);
  border: 1px solid #e1e6f0;
  max-width: 600px;
}

.form-title {
  font-size: 1.3rem;
  font-weight: 500;
  color: #2c3e50;
  margin-bottom: 20px;
  text-align: center;
}

.add-item-form .form-group {
  margin-bottom: 18px;
}

.add-item-form label {
  display: block;
  font-weight: 500;
  margin-bottom: 8px;
  color: #2c3e50;
}

.add-item-form input {
  width: 100%;
  padding: 10px 15px;
  border: 1px solid #ced4da;
  border-radius: 5px;
  transition: border-color 0.3s;
  font-size: 1rem;
}

.add-item-form input:focus {
  border-color: #6c9bd9;
  outline: none;
  box-shadow: 0 0 0 3px rgba(108, 155, 217, 0.15);
}

.add-item-button {
  background-color: #19728a;
  color: white;
  border: none;
  padding: 12px 20px;
  border-radius: 5px;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.3s;
  width: 100%;
  margin-top: 8px;
}

.add-item-button:hover {
  background-color: #1a8ca6;
}

.add-toggle-button {
  background-color: #19728a;
  color: white;
  border: none;
  padding: 10px 16px;
  border-radius: 5px;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.3s;
  margin-bottom: 15px;
}

.add-toggle-button:hover {
  background-color: #1a8ca6;
}
</style> 