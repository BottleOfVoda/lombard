<template>
  <!-- Оставляем только main контент, так как хедер/футер в App.vue -->
  <main class="container content">
    <h2>Ваши забронированные товары</h2>
   

    <!-- Сообщение об ошибке загрузки -->
    <div v-if="errorMessage" class="error-message">
      {{ errorMessage }}
    </div>

    <!-- Индикатор загрузки -->
    <div v-if="isLoading" class="loading-message">
      Загрузка корзины...
    </div>

    <!-- Блок сортировки и поиска -->
    <div v-if="!isLoading && !errorMessage && allItems.filter(i => i.is_booked).length > 0" class="filter-sort-controls">
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

    <!-- Сетка забронированных товаров (показывать только если нет загрузки и ошибок) -->
    <div v-if="!isLoading && !errorMessage" class="product-grid">
      <!-- Отображаем отфильтрованные и отсортированные товары -->
      <div v-if="filteredAndSortedBookedItems.length > 0" class="product-card" v-for="item in filteredAndSortedBookedItems" :key="item.id">
         <!-- Используем item.image_url -->
        <img :src="item.image_url || 'https://via.placeholder.com/200x150.png/eee/aaa?text=No+Image'" :alt="item.name" class="product-image">
        <h3 class="product-name">{{ item.name }}</h3>
         <!-- Используем item.price -->
        <p class="product-price">Цена: {{ item.price }}р</p>
        
        <!-- Здесь всегда должна быть галочка (кнопка снятия брони), так как мы показываем только bookedItems -->
        <div 
          class="booked-indicator" 
          title="Снять бронь" 
          @click="unbookItem(item)" 
          :style="{ cursor: bookingState[item.id] === 'loading' ? 'wait' : 'pointer' }" >
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
      <!-- Сообщение, если после фильтрации/поиска товаров не найдено -->
      <div v-else-if="searchQuery && filteredAndSortedBookedItems.length === 0" class="empty-message">
        По вашему запросу "{{ searchQuery }}" ничего не найдено среди забронированных товаров.
      </div>
      <!-- Сообщение, если корзина пуста изначально -->
      <div v-else class="empty-message">
         У вас нет забронированных товаров.
      </div>
    </div>

    <!-- Блок действий (перемещен сюда) -->
    <div v-if="!isLoading && !errorMessage && filteredAndSortedBookedItems.length > 0" class="action-controls">
      <!-- Кнопка Создать бронь -->
      <button @click="confirmBooking" :disabled="isConfirmingBooking || isDownloadingPdf" class="confirm-button">
        {{ isConfirmingBooking ? 'Подтверждение...' : 'Создать бронь' }}
      </button>
      
      <!-- Сообщения -->
      <p v-if="bookingSuccessMessage" class="success-message">{{ bookingSuccessMessage }}</p>
      <p v-if="pdfError" class="error-message">{{ pdfError }}</p>
    </div>
  </main>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'; // Добавляем computed
import axios from 'axios';
import config from './config';

// Состояние для хранения ВСЕХ товаров (для фильтрации)
const allItems = ref([]); 
const isLoading = ref(false);
const errorMessage = ref(null);
// Состояние для отслеживания процесса снятия брони
const bookingState = ref({}); // { itemId: 'loading' | 'error', ... }

// Ref для хранения выбранной сортировки
const sortOption = ref('default');

// Новые refs для скачивания PDF
const isDownloadingPdf = ref(false);
const pdfError = ref(null);

// Новые refs для подтверждения брони
const isConfirmingBooking = ref(false);
const bookingSuccessMessage = ref('');

// Ref для поиска
const searchQuery = ref('');

// Вычисляемое свойство для фильтрации и СОРТИРОВКИ забронированных товаров
const filteredAndSortedBookedItems = computed(() => {
  // 1. Фильтруем все товары, оставляя только забронированные
  let filtered = allItems.value.filter(item => item.is_booked === true);
  
  // 2. Фильтруем по поисковому запросу (если он есть)
  if (searchQuery.value) {
    const lowerCaseQuery = searchQuery.value.toLowerCase();
    filtered = filtered.filter(item =>
      item.name && item.name.toLowerCase().includes(lowerCaseQuery)
    );
  }
  
  // 3. Сортируем отфильтрованный массив
  let sorted = [...filtered]; 
  switch (sortOption.value) {
    case 'name_asc':
      sorted.sort((a, b) => (a.name || '').localeCompare(b.name || ''));
      break;
    case 'price_asc':
      sorted.sort((a, b) => Number(a.price || 0) - Number(b.price || 0));
      break;
    case 'price_desc':
      sorted.sort((a, b) => Number(b.price || 0) - Number(a.price || 0));
      break;
  }
  
  return sorted;
});

// Асинхронная функция для загрузки товаров с бэкенда
const fetchItems = async () => {
  isLoading.value = true;    // Начинаем загрузку
  errorMessage.value = null; // Сбрасываем предыдущие ошибки
  try {
    // Делаем GET-запрос к нашему API
    const response = await axios.get(`${config.API_URL}/api/products`);
    // Записываем полученные данные в items (все товары)
    allItems.value = response.data;
  } catch (error) {
    console.error("Ошибка при загрузке товаров для корзины:", error);
    if (error.response) {
        errorMessage.value = `Ошибка сервера: ${error.response.data.message || error.response.status}`;
    } else if (error.request) {
        errorMessage.value = "Не удалось подключиться к серверу.";
    } else {
        errorMessage.value = "Произошла ошибка при запросе товаров.";
    }
  } finally {
    isLoading.value = false; 
  }
};

// --- Метод для СНЯТИЯ брони товара (копируем из Goods.vue) ---
const unbookItem = async (item) => {
  if (bookingState.value[item.id] === 'loading') return;
  
  bookingState.value = { ...bookingState.value, [item.id]: 'loading' };
  let bookingError = null; 

  try {
    await axios.put(`${config.API_URL}/api/products/${item.id}/unbook`);
    // Обновляем состояние товара ЛОКАЛЬНО во ВСЕХ товарах
    const index = allItems.value.findIndex(i => i.id === item.id);
    if (index !== -1) {
      allItems.value[index].is_booked = false;
      // Computed свойство filteredAndSortedBookedItems автоматически обновится
    }
    const newBookingState = { ...bookingState.value };
    delete newBookingState[item.id];
    bookingState.value = newBookingState;
  } catch (error) {
    console.error(`Ошибка при снятии брони с товара ${item.id}:`, error);
     if (error.response) {
        bookingError = `Ошибка сервера: ${error.response.data.message || error.response.status}`;
    } else if (error.request) {
        bookingError = "Не удалось подключиться к серверу для снятия брони.";
    } else {
        bookingError = "Произошла ошибка при запросе снятия брони.";
    }
    bookingState.value = { ...bookingState.value, [item.id]: 'error' };
    alert(bookingError);
  }
};

// --- Функция для скачивания PDF --- 
const downloadBookedPdf = async () => {
  isDownloadingPdf.value = true;
  pdfError.value = null;

  try {
    // Отправляем GET-запрос на эндпоинт генерации PDF
    // Важно указать responseType: 'blob', чтобы получить файл
    const response = await axios.get(`${config.API_URL}/api/generate-booked-pdf`, {
      responseType: 'blob', 
    });

    // Создаем URL для скачивания из полученного blob
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;

    // Пытаемся получить имя файла из заголовка Content-Disposition
    let filename = 'booked_items_report.pdf'; // Имя по умолчанию
    const disposition = response.headers['content-disposition'];
    if (disposition && disposition.indexOf('attachment') !== -1) {
      const filenameRegex = /filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/;
      const matches = filenameRegex.exec(disposition);
      if (matches != null && matches[1]) { 
        filename = matches[1].replace(/['"]/g, '');
      }
    }

    link.setAttribute('download', filename);
    document.body.appendChild(link);
    link.click(); // Инициируем скачивание

    // Очищаем после скачивания
    link.remove();
    window.URL.revokeObjectURL(url);

  } catch (error) {
    console.error("Ошибка при скачивании PDF:", error);
    if (error.response) {
        // Если бэкенд вернул JSON с ошибкой (например, 404 - нет товаров)
        // то response.data будет не blob, а ArrayBuffer или что-то еще.
        // Попробуем прочитать ошибку как JSON, если возможно
        try {
          // Конвертируем ArrayBuffer в строку, потом в JSON
          const errorData = JSON.parse(new TextDecoder().decode(await error.response.data)); 
          pdfError.value = `Ошибка сервера: ${errorData.message || error.response.status}`;
        } catch (parseError) {
          // Если не удалось распарсить JSON, показываем общую ошибку
          pdfError.value = `Ошибка сервера: ${error.response.status} ${error.response.statusText || ''}`;
        }
    } else if (error.request) {
        pdfError.value = "Не удалось подключиться к серверу для скачивания PDF.";
    } else {
        pdfError.value = "Произошла ошибка при запросе PDF-отчета.";
    }
  } finally {
    isDownloadingPdf.value = false;
  }
};

// --- Функция подтверждения брони --- 
const confirmBooking = async () => {
  isConfirmingBooking.value = true;
  bookingSuccessMessage.value = ''; // Сбрасываем старое сообщение
  pdfError.value = null; // Сбрасываем ошибку PDF перед новой попыткой
  
  try {
    // Вызываем функцию скачивания PDF
    await downloadBookedPdf();

    // Проверяем, не возникла ли ошибка при скачивании PDF
    if (pdfError.value) {
      // Ошибка уже установлена в downloadBookedPdf, ничего не делаем
      console.log('Booking confirmation failed because PDF download failed.');
    } else {
      // Если ошибки PDF нет, значит скачивание инициировано
      bookingSuccessMessage.value = 'Бронь успешно создана! Отчет PDF загружается.';
      // Опционально: можно скрыть сообщение через несколько секунд
      setTimeout(() => { bookingSuccessMessage.value = ''; }, 5000); 
    }
  } catch (error) {
      // Сюда мы не должны попасть, так как downloadBookedPdf обрабатывает свои ошибки
      // Но на всякий случай:
      console.error("Unexpected error during booking confirmation:", error);
      pdfError.value = "Неожиданная ошибка при подтверждении брони.";
  } finally {
      isConfirmingBooking.value = false;
  }
};

// Вызываем функцию загрузки товаров при монтировании компонента
onMounted(() => {
  fetchItems();
});

</script>

<style scoped>
/* Стили копируем из Goods.vue, но убираем кнопку .add-button, 
   так как здесь ее не будет. Оставляем .booked-indicator */

.container { /* ... */ }
.content { /* ... */ }
.page-title { /* ... */ }
.product-grid {
  display: grid;
  /* Устанавливаем 3 колонки */
  grid-template-columns: repeat(3, 1fr);
  gap: 30px; /* Можно оставить или изменить отступ */
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
  /* ... */
}
.product-image {
  max-width: 100%;
  height: 180px; /* Устанавливаем высоту */
  object-fit: contain;
  margin-bottom: 15px;
}
.product-name {
  font-size: 1.2rem; /* Устанавливаем размер */
  font-weight: 500;
  margin-bottom: 8px;
  color: #333; /* Устанавливаем цвет */
}
.product-price {
  font-size: 1.1rem; /* Устанавливаем размер */
  color: #333; /* Устанавливаем цвет */
  margin-bottom: 15px;
}

.booked-indicator {
  position: absolute;
  bottom: 15px;
  right: 15px;
  padding: 5px;
  cursor: pointer; /* Добавим для ясности */
}

.booked-indicator svg {
  width: 24px;
  height: 24px;
}

/* Стили сообщений */
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
  grid-column: 1 / -1; /* Занять всю ширину грида */
}

/* Адаптивные стили */
@media (max-width: 768px) {
  .product-grid {
    grid-template-columns: repeat(2, 1fr); /* 2 колонки */
  }
}

@media (max-width: 480px) {
  .product-grid {
    grid-template-columns: 1fr; /* 1 колонка */
  }
}

/* Правило для 1024px и выше больше не нужно, удаляем его или комментируем */
/*
@media (min-width: 1024px) {
  .product-grid {
    grid-template-columns: repeat(4, 1fr);
  }
}
*/

/* Стили для блока сортировки и поиска */
.filter-sort-controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 20px;
  margin-bottom: 30px; /* Отступ до сетки */
  padding: 15px;
  background-color: #f8f9fa;
  border-radius: 6px;
}

.search-control input[type="search"] {
  padding: 8px 12px;
  border: 1px solid #ced4da;
  border-radius: 4px;
  min-width: 250px;
}

.sort-control label {
  margin-right: 8px;
  color: #000; 
}

.sort-control select {
  padding: 8px 10px;
  border: 1px solid #ced4da;
  border-radius: 4px;
}

/* Контейнер для кнопок действий (теперь под сеткой) */
.action-controls {
  text-align: center; 
  margin-top: 40px; /* Увеличим отступ сверху от сетки */
  margin-bottom: 30px; 
  /* padding-bottom: 20px; */ /* Убрали паддинг */
  /* border-bottom: 1px solid #eee; */ /* Убрали разделитель */
  display: flex; 
  flex-direction: column; 
  align-items: center; 
  gap: 15px; 
}

/* Общие стили для кнопок действий */
.action-controls button {
  padding: 10px 25px;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-size: 1.05rem;
  transition: background-color 0.3s ease, opacity 0.3s ease;
  min-width: 200px; /* Минимальная ширина кнопок */
}

/* Стили для кнопки "Создать бронь" */
.confirm-button {
  background-color: #28a745; /* Зеленый */
}
.confirm-button:hover {
  background-color: #218838;
}

/* Стили для отключенных кнопок */
.action-controls button:disabled {
  background-color: #aaa;
  cursor: not-allowed;
  opacity: 0.7;
}

/* Сообщения */
.action-controls .error-message, 
.action-controls .success-message {
  font-size: 0.95rem;
  margin-top: 5px; /* Уменьшим отступ */
}

.success-message {
  color: green;
  font-weight: bold;
}

/* Убираем дублирующийся стиль для ошибки PDF */
/* .download-controls .error-message {...} */

/* Добавляем стили для заголовка страницы H2 */
.container.content h2 {
  text-align: center; /* Выравниваем по центру */
  color: #333; /* Темный цвет */
  margin-bottom: 30px; /* Отступ снизу */
  font-weight: 500; /* Средняя жирность */
}

</style> 