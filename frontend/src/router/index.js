import { createRouter, createWebHistory } from 'vue-router'
import DiningHallsView from '../views/DiningHallsView.vue'
import MealPlannerView from '../views/MealPlannerView.vue'
import CampusMapView from '../views/CampusMapView.vue'
import ChatbotView from '../views/ChatbotView.vue'
import OnboardingView from '../views/OnboardingView.vue'
import Profile from '../views/Profile.vue'

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
      path: '/chatbot',
      name: 'chatbot',
      component: ChatbotView
    },
    {
      path: '/onboarding',
      name: 'onboarding',
      component: OnboardingView,
      meta: { hideNav: true }
    },
    {
      path: '/profile',
      name: 'profile',
      component: Profile
    }
  ]
})

export default router
