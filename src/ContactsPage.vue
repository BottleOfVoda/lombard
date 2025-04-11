<template>
  <main class="container content">
    <h1 class="page-title">Контакты</h1>
    <p>Наш адрес: Лермонтовский просп., 4, Санкт-Петербург</p>
    
    <!-- Контейнер для Яндекс.Карты -->
    <div id="yandex-map">
      <!-- Сообщение будет вставлено здесь в случае ошибки -->
    </div>

    <!-- Добавляем контактную информацию -->
    <div class="contact-info">
      <p>Наша почта: <a href="mailto:LombardAvangard@gmail.com">LombardAvangard@gmail.com</a></p>
      <p>Наш телефон: <a href="tel:+78123226060">+7 (812) 322-60-60</a></p>
    </div>
  </main>
</template>

<script setup>
import { onMounted, ref } from 'vue';

const ymaps = ref(null); // Хранилище для объекта ymaps после загрузки

// Вспомогательная функция для отображения сообщений внутри контейнера карты
const showMapMessage = (message, type = 'error') => {
  const mapDiv = document.getElementById('yandex-map');
  if (mapDiv) {
    const color = type === 'error' ? 'red' : (type === 'warning' ? 'darkorange' : 'black');
    // Используем шаблонные строки для читаемости и правильной обработки кавычек
    mapDiv.innerHTML = `<p style="text-align: center; color: ${color};">${message}</p>`;
  }
};

// Функция для загрузки API Яндекс.Карт
const loadYandexMapsAPI = () => {
  return new Promise((resolve, reject) => {
    // Проверяем, не был ли API загружен ранее
    if (window.ymaps) {
      console.log('Yandex Maps API already loaded.');
      ymaps.value = window.ymaps;
      resolve(window.ymaps);
      return;
    }

    const script = document.createElement('script');
    // ВАЖНО: Замените YOUR_API_KEY на ваш действительный API-ключ!
    const apiKey = 'b0525f98-2e54-474a-8f5d-cc4765f1d553'; // <-- Убедись, что здесь твой ключ
    console.log('Using API Key:', apiKey); // Оставляем лог для проверки

    // Упрощенная проверка: только на пустое значение
    if (!apiKey) { // Сработает только если apiKey пустой, null или undefined
        const msg = 'Не удалось загрузить карту: API-ключ Яндекс.Карт не указан или пуст.';
        console.warn(msg);
        showMapMessage(msg, 'error');
        reject('API key not provided or empty');
        return;
    }

    // Если мы дошли сюда, значит ключ есть
    console.log('API Key check passed. Proceeding to load script...');

    script.src = `https://api-maps.yandex.ru/2.1/?apikey=${apiKey}&lang=ru_RU`;
    script.type = 'text/javascript';
    script.async = true; // Асинхронная загрузка
    
    script.onload = () => {
      // ymaps.ready гарантирует полную инициализацию API
      window.ymaps.ready(() => {
        console.log('Yandex Maps API loaded and ready.');
        ymaps.value = window.ymaps;
        resolve(window.ymaps);
      });
    };
    
    script.onerror = (error) => {
        const msg = 'Ошибка при загрузке скрипта Яндекс.Карт.';
        console.error(msg, error);
        showMapMessage(msg, 'error');
        reject(error);
    };
    
    // Добавляем скрипт в head
    document.head.appendChild(script);
  });
};

// Функция инициализации карты
const initMap = async () => {
  let ymapsInstance;
  try {
    // Убедимся, что контейнер карты существует в DOM
    const mapDiv = document.getElementById('yandex-map');
    if (!mapDiv) {
      console.error('Контейнер карты #yandex-map не найден.');
      return; 
    }
    
    // Показываем индикатор загрузки
    showMapMessage('Загрузка карты...', 'info'); 
    
    ymapsInstance = await loadYandexMapsAPI();
    
    const address = 'Лермонтовский просп., 4, Санкт-Петербург';

    // 1. Геокодируем адрес
    console.log(`Geocoding address: ${address}`);
    const geocoder = ymapsInstance.geocode(address);
    
    // Ожидаем результат геокодирования
    const res = await geocoder; 
    
    const firstGeoObject = res.geoObjects.get(0);
    if (!firstGeoObject) {
        const msg = `Не удалось найти координаты для адреса: ${address}`;
        console.error(msg);
        showMapMessage(msg, 'warning');
        return;
    }
    const coords = firstGeoObject.geometry.getCoordinates();
    const addressDetails = firstGeoObject.getAddressLine(); // Уточненный адрес
    console.log(`Coordinates found: ${coords}`);

    // Очищаем сообщение о загрузке перед созданием карты
    mapDiv.innerHTML = ''; 

    // 2. Создаем карту
    console.log('Creating map...');
    const myMap = new ymapsInstance.Map('yandex-map', {
        center: coords,
        zoom: 16, // Масштаб
        controls: ['zoomControl', 'fullscreenControl'] // Элементы управления
    });

    // 3. Создаем и добавляем метку (Placemark)
    const placemark = new ymapsInstance.Placemark(coords, {
        // Содержимое балуна (открывается по клику)
        balloonContentBody: addressDetails,
        // Всплывающая подсказка при наведении
        hintContent: address
    }, {
        preset: 'islands#redDotIcon' // Стандартная красная метка
    });

    myMap.geoObjects.add(placemark);
    
    // Отключаем масштабирование колесиком мыши (часто мешает прокрутке страницы)
    myMap.behaviors.disable('scrollZoom');
    console.log('Map initialized successfully.');

  } catch (error) {
    // Ошибки типа "API key not provided" или ошибка загрузки скрипта уже обработаны
    // и должны были показать сообщение через showMapMessage.
    // Этот блок перехватывает другие ошибки (например, отказ промиса geocode).
    console.error('Не удалось инициализировать карту:', error);
    // Показываем общее сообщение об ошибке, только если еще нет другого сообщения
    const mapDiv = document.getElementById('yandex-map');
    if (mapDiv && !mapDiv.querySelector('p')) { // Проверяем, есть ли уже тег <p> с сообщением
       showMapMessage('Произошла ошибка при инициализации карты.', 'error');
    }
  }
};

onMounted(() => {
  // Убедимся, что код выполняется в браузере
  if (typeof window !== 'undefined') {
      initMap();
  }
});

</script>

<style scoped>
.page-title {
  text-align: center;
  margin-bottom: 20px;
  color: #333; /* Добавляем темный цвет для заголовка */
}

#yandex-map {
  width: 100%;
  height: 450px; /* Высота карты */
  border: 1px solid #ccc;
  margin-top: 20px;
  margin-bottom: 20px;
  background-color: #f8f8f8; /* Светлый фон для контейнера */
  display: flex; /* Используем flex для центрирования сообщений */
  justify-content: center;
  align-items: center;
  overflow: hidden; /* Предотвращаем возможные проблемы с переполнением */
}

/* Стили для сообщений внутри карты (ошибки, загрузка) */
/* Мы используем style="...", но можно и так */
/*
#yandex-map p {
    margin: 0;
    padding: 20px; 
    text-align: center; 
}
*/

/* Стили для основного контента страницы (параграф с адресом) */
.container.content > p:first-of-type { /* Более точный селектор для адреса */
  color: #333; 
  margin-bottom: 20px;
}

/* Стили для блока с контактной информацией */
.contact-info {
  margin-top: 20px; /* Отступ сверху от карты */
  text-align: left; /* Выравнивание по левому краю */
}

.contact-info p {
  color: #333; /* Темный цвет текста */
  margin-bottom: 10px; /* Отступ между строками */
  line-height: 1.6; /* Межстрочный интервал */
}

.contact-info a {
  color: #007bff; /* Стандартный синий цвет для ссылок */
  text-decoration: none; /* Убираем подчеркивание по умолчанию */
}

.contact-info a:hover {
  text-decoration: underline; /* Добавляем подчеркивание при наведении */
}

</style> 