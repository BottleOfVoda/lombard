import { createRouter, createWebHistory } from 'vue-router'
import AuthPade from '../AuthPade.vue'
import RegistrPade from '../RegistrPade.vue'
import Goods from '../Goods.vue' // Assuming Goods.vue is directly in src, adjust if it's elsewhere like src/views
import UserProfile from '../UserProfile.vue'
import BookingCart from '../BookingCart.vue'
import ContactsPage from '../ContactsPage.vue'

const routes = [
  {
    path: '/',
    name: 'Login', // Имя маршрута для удобства
    component: AuthPade
  },
  {
    path: '/register',
    name: 'Register',
    component: RegistrPade
  },
  {
    path: '/goods',
    name: 'Goods',
    component: Goods
  },
  {
    path: '/profile',
    name: 'Profile',
    component: UserProfile
  },
  {
    path: '/booking',
    name: 'BookingCart',
    component: BookingCart
  },
  {
    path: '/contacts',
    name: 'Contacts',
    component: ContactsPage
  },
  { path: '/:pathMatch(.*)*', redirect: '/' }
]

const router = createRouter({
  // Используем history mode для чистых URL без #
  history: createWebHistory(import.meta.env.BASE_URL), // Используем Base URL из Vite
  routes, // сокращение для `routes: routes`
})

export default router 