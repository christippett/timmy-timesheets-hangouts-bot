import Vue from 'vue'
import Router from 'vue-router'
import HelloWorld from '@/components/HelloWorld'
import RegisterError from '@/components/RegisterError'
import RegisterConfig from '@/components/RegisterConfig'

Vue.use(Router)

export default new Router({
  mode: 'history',
  routes: [
    {
      path: '/',
      name: 'HelloWorld',
      component: HelloWorld
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
