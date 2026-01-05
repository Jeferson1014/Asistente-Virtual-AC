import { createRouter, createWebHistory } from 'vue-router';
import LandingPage from '../components/LandingPage.vue';
import MicControl from '../components/MicControl.vue';
import AsistentePsicologico from '../components/AsistentePsicologico.vue'; // Componente del asistente

const routes = [
  {
    path: '/',
    name: 'Inicio',
    component: LandingPage
  },
  {
    path: '/asistente-psicologico',
    name: 'AsistentePsicologico',
    component: AsistentePsicologico
  },
  {
    path: '/mic-control',
    name: 'MicControl',
    component: MicControl
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

export default router;
