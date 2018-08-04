import Vue from 'vue'
import Router from 'vue-router'
import HomePage from '@/components/HomePage'
import RegisterError from '@/components/RegisterError'
import RegisterConfig from '@/components/RegisterConfig'

Vue.use(Router)

export default new Router({
  mode: 'history',
  linkExactActiveClass: 'is-active',
  routes: [
    {
      path: '/',
      name: 'HomePage',
      component: HomePage
    },
    {
      path: '/register/error',
      name: 'RegisterError',
      component: RegisterError
    },
    {
      path: '/register/config',
      name: 'RegisterConfig',
      component: RegisterConfig
    }
  ]
})
