import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import InterviewView from '../views/InterviewView.vue'

export default createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'home', component: HomeView },
    {
      path: '/questions/:id(\\d+)',
      name: 'interview',
      component: InterviewView,
      props: (route) => ({ id: Number(route.params.id) }),
    },
    { path: '/:pathMatch(.*)*', redirect: '/' },
  ],
})
