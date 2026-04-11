import { createRouter, createWebHistory } from 'vue-router'
import DiningHallsView from '../views/DiningHallsView.vue'
import MealPlannerView from '../views/MealPlannerView.vue'
import CampusMapView from '../views/CampusMapView.vue'
import ConnectView from '../views/ConnectView.vue'
import CallbackView from '../views/CallbackView.vue'
import Login from '../views/Login.vue'
import OnboardingView from '../views/OnboardingView.vue'
import { useAuthStore } from '@/stores/auth'
import { getProfile } from '@/api'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: Login,
      meta: { hideNav: true, public: true }
    },
    {
      path: '/onboarding',
      name: 'onboarding',
      component: OnboardingView,
      meta: { hideNav: true }
    },
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
      path: '/calendar-callback',
      name: 'calendar-callback',
      component: CallbackView,
      meta: { hideNav: true }
    }
  ]
})

// Navigation Guard
router.beforeEach(async (to, from, next) => {
  const auth = useAuthStore()
  
  if (!to.meta.public && !auth.isAuthenticated) {
    return next('/login')
  }
  
  if (auth.isAuthenticated && to.name !== 'onboarding' && to.name !== 'login') {
    try {
      await getProfile() 
      // Profile exists, let them pass
    } catch (e) {
      // 404 meaning no profile yet
      if (e.response?.status === 404) {
        return next('/onboarding')
      }
    }
  }

  if (to.name === 'login' && auth.isAuthenticated) {
    return next('/')
  }
  
  next()
})

export default router
