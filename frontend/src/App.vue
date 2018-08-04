<template>
  <div id="app">
    <section class="hero is-fullheight is-default is-bold">
      <div class="hero-head">
        <nav-bar></nav-bar>
      </div>
      <div class="hero-body">
        <!-- <img width="200" src="./assets/logo.png"> -->
        <router-view/>
      </div>

      <div class="hero-foot">
        <div class="container">
          <div class="tabs is-centered">
            <ul>
              <li>
                <a>Footer</a>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script>
import NavBar from '@/components/NavBar'

export default {
  name: 'App',
  data () {
    return {
      navbarActive: false
    }
  },
  components: {
    NavBar
  }
}
</script>

<style>
#app {
  font-family: 'Open Sans', serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
}
img.logo {
  max-height: 1rem;
}
</style>
