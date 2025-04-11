<template>
  <div class="auth-container">
    <div class="left-panel">
      <h1>Ломбард Авангард</h1>
    </div>
    <div class="right-panel">
      <h2>Регистрация</h2>
      <form @submit.prevent="register">
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
        <div class="form-group">
          <label for="fullName">ФИО</label>
          <input type="text" id="fullName" v-model="fullName" placeholder="Фамилия Имя Отчество">
        </div>
        <div class="form-group">
          <label for="phoneNumber">Номер телефона</label>
          <input type="tel" id="phoneNumber" v-model="phoneNumber" placeholder="+7 (XXX) XXX-XX-XX">
        </div>
        <div class="form-group">
          <label for="email">Электронная почта</label>
          <input type="email" id="email" v-model="email" placeholder="your@email.com" required>
        </div>
        <button type="submit" class="button-next">Зарегистрироваться</button>
      </form>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import config from './config';

export default {
  name: 'RegisterPage',
  data() {
    return {
      username: '',
      password: '',
      fullName: '',
      phoneNumber: '',
      email: '',
      errorMessage: null,
      successMessage: null,
      isLoading: false
    };
  },
  methods: {
    async register() {
      this.errorMessage = null;
      this.successMessage = null;
      this.isLoading = true;
      
      if (!this.username || !this.password || !this.email) {
          this.errorMessage = 'Пожалуйста, заполните Логин, Пароль и Email.';
          return;
      }

      try {
        const response = await axios.post(`${config.API_URL}/api/register`, {
          username: this.username,
          password: this.password,
          email: this.email,
          fullName: this.fullName,
          phoneNumber: this.phoneNumber
        });

        this.successMessage = response.data.message;
        alert(`Успех: ${response.data.message}`);

        this.username = '';
        this.password = '';
        this.fullName = '';
        this.phoneNumber = '';
        this.email = '';
        this.$router.push('/login');

      } catch (error) {
        if (error.response) {
          this.errorMessage = error.response.data.message || 'Произошла ошибка при регистрации.';
          alert(`Ошибка: ${this.errorMessage}`);
        } else if (error.request) {
          this.errorMessage = 'Не удалось подключиться к серверу. Попробуйте позже.';
          alert(`Ошибка: ${this.errorMessage}`);
        } else {
          this.errorMessage = 'Произошла непредвиденная ошибка.';
          console.error('Register error:', error.message);
          alert(`Ошибка: ${this.errorMessage}`);
        }
      } finally {
        this.isLoading = false;
      }
    }
  },
};
</script>

<style scoped>
.auth-container {
  display: flex;
  height: 100vh; /* Full viewport height */
  width: 100vw; /* Full viewport width */
  margin: 0;
  padding: 0;
  box-sizing: border-box; /* Include padding and border in element's total width and height */
  overflow: hidden; /* Prevent scrollbars if content overflows */
  position: fixed; /* Fix position relative to viewport */
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

/* Generic Button Styles (apply to both) */
.button-register,
.button-next {
  padding: 12px 25px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1rem;
  font-weight: bold; /* Ensure both are bold like original button */
  transition: background-color 0.3s ease;
  color: white; /* Assuming white text for both initially */
  background-color: #222; /* Dark background for both initially */
}

.button-register {
  float: left;
}

.button-next {
  float: right;
}

/* Hover effects */
.button-register:hover,
.button-next:hover {
  background-color: #444; /* Default hover */
}

/* Ensure form element takes full width to allow button floating */
form {
    width: 100%;
    max-width: 350px;
}

/* Clearfix for the form to contain the floated buttons */
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
    position: static;
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

   /* Remove clearfix in mobile view as floats are cleared */
   form::after {
     display: none;
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