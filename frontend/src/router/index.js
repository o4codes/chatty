import { createRouter, createWebHistory } from 'vue-router'
import HomePage from '../views/HomePage.vue'
import RoomPage from '../views/RoomPage.vue'

const routes = [
  { path: '/', name: 'home', component: HomePage },
  { path: '/room/:id', name: 'room', component: RoomPage, props: true },
  { path: '/:pathMatch(.*)*', name: 'not-found', redirect: '/' },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
