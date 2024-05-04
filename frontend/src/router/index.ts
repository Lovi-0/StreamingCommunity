import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import Details from "../views/Details.vue";

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView
    },
      {
      path: '/details:item:imageUrl',
      name: 'details',
      component: Details,
      props: route => {
        let item;
        try {
          item = JSON.parse(<string>route.params.item);
        } catch (error) {
          item = {}; // default value
        }
        return { item: item, imageUrl: route.params.imageUrl };
      },
    }
  ]
})

export default router
