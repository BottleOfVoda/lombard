<template>
  <div class="auth-container">
    <div class="left-panel">
      <h1>Ломбард Авангард</h1>
    </div>
    <div class="right-panel">
      <h2>Авторизация</h2>
      <form @submit.prevent="login">
        <div v-if="errorMessage" class="error-message">{{ errorMessage }}</div>
        <div v-if="successMessage" class="success-message">{{ successMessage }}</div>
        <div class="form-group">
          <label for="login">Логин</label>
          <input type="text" id="login" v-model="username" placeholder="Логин">
        </div>
        <div class="form-group">
          <label for="password">Пароль</label>
          <input type="password" id="password" v-model="password" placeholder="Пароль">
        </div>
        <button type="button" @click="goToRegister" class="button-register">Зарегистрироваться</button>
        <button type="submit" class="button-next">Войти</button>
      </form>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import config from './config';

export default {
  name: 'AuthPage',
  data() {
    return {
      username: '',
      password: '',
      errorMessage: null,
      successMessage: null
    };
  },
  methods: {
    async login() {
      console.log('Router instance:', this.$router);
      console.log('Login method triggered by form submit');
      this.errorMessage = null;
      this.successMessage = null;
      
      if (!this.username || !this.password) {
          this.errorMessage = 'Пожалуйста, введите логин и пароль.';
          console.log('Validation failed: Missing username or password.'); 
          return;
      }
      
      console.log('Attempting API call to /api/login');
      try {
        const response = await axios.post(`${config.API_URL}/api/login`, {
          username: this.username,
          password: this.password
        });
        console.log('API call successful. Response data:', response.data);

        if (!response.data || response.data.user_id === undefined) {
             console.error('Error: Missing user_id in server response.');
             this.errorMessage = 'Ошибка ответа сервера: отсутствует ID пользователя.';
             return; 
        }
        if (response.data.role === undefined) {
            console.warn('Warning: Missing user_role in server response.');
        }

        console.log('Attempting to save user_id to localStorage:', response.data.user_id);
        localStorage.setItem('user_id', response.data.user_id);
        console.log('user_id saved. Attempting to save user_role:', response.data.role);
        localStorage.setItem('user_role', response.data.role);
        console.log('user_role saved.');

        console.log('Attempting router push to /goods');
        await this.$router.push('/goods');
        console.log('Router push called successfully.');

      } catch (error) {
        console.error('Error during login API call or processing:', error);
        if (error.response) {
          console.error('Server responded with error:', error.response.data, error.response.status);
          this.errorMessage = error.response.data.message || 'Произошла ошибка при входе.';
        } else if (error.request) {
          console.error('No response received from server:', error.request);
          this.errorMessage = 'Не удалось подключиться к серверу. Попробуйте позже.';
        } else {
          console.error('Error setting up the request:', error.message);
          this.errorMessage = 'Произошла непредвиденная ошибка.';
        }
      }
    },
    goToRegister() {
      this.$router.push('/register');
    },
  },
};
</script>

<style scoped>
.auth-container {
  display: flex;
  height: 100vh; /* Возвращаем */
  width: 100vw; /* Возвращаем */
  margin: 0;
  padding: 0;
  box-sizing: border-box;
  overflow: hidden; /* Возвращаем */
  position: fixed; /* Возвращаем */
  top: 0;
  left: 0;
}

.left-panel {
  flex: 1; /* Take up half the space */
  background: linear-gradient(to bottom right, #031027, #19728a, #37e5b4); /* Purple gradient */
  color: white;
  display: flex;
  justify-content: center;
  align-items: center;
  text-align: center;
  padding: 20px;
  background: linear-gradient(135deg, #031027 0%, #19728a 40%, #37e5b4 100%); /* Darker purple gradient */
}

.left-panel h1 {
  font-size: 4rem; /* Larger font size */
  font-weight: bold;
}

.right-panel {
  flex: 1; /* Take up the other half */
  background-color: #ffffff; /* Very light pink/off-white */
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  padding: 40px;
}

.right-panel h2 {
  font-size: 2.5rem;
  margin-bottom: 30px;
  color: #333;
}

.form-group {
  margin-bottom: 20px;
  width: 100%;
  max-width: 350px; /* Limit form width */
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  color: #555;
  font-size: 1rem;
  text-align: left;
}

.form-group input {
  width: 100%;
  padding: 12px 15px;
  border: 1px solid #ccc;
  border-radius: 4px;
  box-sizing: border-box; /* Ensure padding doesn't add to width */
  font-size: 1rem;
}

.form-group input::placeholder {
    color: #aaa;
}

/* Generic Button Styles */
.button-register,
.button-next {
  padding: 12px 25px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1rem;
  font-weight: bold;
  transition: background-color 0.3s ease;
  color: white;
  background-color: #222;
  /* Убираем стили блочного расположения */
  /* display: block; */
  /* width: 100%; */
  /* margin-top: 15px; */
  /* box-sizing: border-box; */
}

/* Возвращаем float */
.button-register {
  float: left;
}

/* Возвращаем float */
.button-next {
  float: right;
}

/* Убираем контейнер для кнопок */
/* .button-group { ... } */

/* Hover effects */
.button-register:hover,
.button-next:hover {
  background-color: #444; /* Default hover */
}

form {
    width: 100%;
    max-width: 350px;
}

/* Возвращаем clearfix */
form::after {
  content: "";
  clear: both;
  display: table;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .auth-container {
    flex-direction: column;
    height: auto;
  }

  .left-panel, .right-panel {
    flex: none; /* Disable flex grow */
    width: 100%; /* Take full width */
    min-height: 30vh; /* Minimum height for left panel */
  }

  .right-panel {
     min-height: 70vh; /* Minimum height for right panel */
     justify-content: flex-start; /* Align form to top */
     padding-top: 50px;
  }

  .left-panel h1 {
    font-size: 3rem;
  }

  .right-panel h2 {
    font-size: 2rem;
    margin-bottom: 20px;
  }

  .form-group {
      max-width: 80%;
      margin-left: auto;
      margin-right: auto;
  }

  /* Adjust button layout for mobile */
  .button-register,
  .button-next {
      float: none; /* Remove float */
      display: block; /* Make them block level */
      width: 80%;   /* Set width */
      margin: 15px auto 0; /* Center horizontally, add space */
  }
  /* Ensure register button appears above next button */
  .button-register {
      order: 1; /* Lower order appears first in block layout */
      margin-top: 20px; /* Add top margin to first button */
  }
   .button-next {
      order: 2;
      margin-top: 15px; /* Keep vertical space */
   }
}

.error-message {
  color: red;
  margin-bottom: 15px;
}
.success-message {
  color: green;
  margin-bottom: 15px;
}
</style> 