import { createRouter, createWebHistory } from 'vue-router'
import DiningHallsView from '../views/DiningHallsView.vue'
import MealPlannerView from '../views/MealPlannerView.vue'
import CampusMapView from '../views/CampusMapView.vue'
import ConnectView from '../views/ConnectView.vue'
import CallbackView from '../views/CallbackView.vue'
import OnboardingView from '../views/OnboardingView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'dining-halls',
      component: DiningHallsView
    },
    {
      path: '/planner',
      name: 'planner',
      component: MealPlannerView
    },
    {
      path: '/map',
      name: 'campus-map',
      component: CampusMapView
    },
    {
      path: '/connect',
      name: 'connect',
      component: ConnectView
    },
    {
      path: '/onboarding',
      name: 'onboarding',
      component: OnboardingView,
      meta: { hideNav: true }
    },
    {
      path: '/calendar-callback',
      name: 'calendar-callback',
      component: CallbackView,
      meta: { hideNav: true }
    }
  ]
})

export default router
