import { createRouter, createWebHistory } from 'vue-router'
import AttemptView from '../views/AttemptView.vue'
import HistoryView from '../views/HistoryView.vue'
import HomeView from '../views/HomeView.vue'
import InterviewView from '../views/InterviewView.vue'
import CommonView from '../views/CommonView.vue'
import PostingNewView from '../views/PostingNewView.vue'
import PostingView from '../views/PostingView.vue'
import ResumeView from '../views/ResumeView.vue'
import SettingsView from '../views/SettingsView.vue'

const idProp = (route: { params: Record<string, string | string[]> }) => ({ id: Number(route.params.id) })

export default createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'home', component: HomeView },
    { path: '/questions/:id(\\d+)', name: 'interview', component: InterviewView, props: idProp },
    { path: '/history', name: 'history', component: HistoryView },
    { path: '/resume', name: 'resume', component: ResumeView },
    { path: '/settings', name: 'settings', component: SettingsView },
    { path: '/common', name: 'common', component: CommonView },
    { path: '/postings/new', name: 'posting-new', component: PostingNewView },
    { path: '/postings/:id(\\d+)', name: 'posting', component: PostingView, props: idProp },
    { path: '/history/:id(\\d+)', name: 'attempt', component: AttemptView, props: idProp },
    { path: '/:pathMatch(.*)*', redirect: '/' },
  ],
})
