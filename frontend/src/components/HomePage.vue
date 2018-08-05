<template>
  <div class="container has-text-centered">
    <div class="columns is-vcentered">
      <mascot class="column is-5"></mascot>
      <div class="column is-6 is-offset-1">
        <h1 class="title is-2">
          Timmy Timesheets
        </h1>
        <h2 class="subtitle is-4">
          A super helpful chat bot that'll help you with your timesheets. That's the idea, anyway 🤷
        </h2>
        <br>
        <p class="has-text-centered">
          <router-link tag="li" to="/" class="button is-medium is-outlined">
            Learn more
          </router-link>
        </p>
      </div>
    </div>
  </div>
</template>

<script>
import Mascot from '@/components/Mascot'

export default {
  name: 'HelloWorld',
  data () {
    return {
      msg: 'Welcome to Your Vue.js App'
    }
  },
  components: {
    Mascot
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>

</style>
