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
        <div class="container is-size-7">
          <p>Developed by Xavier Clements & Chris Tippett as part of the Melbourne AWS Hackathon.</p>
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
.hero-foot {
  padding: 0.25rem;
}
</style>
