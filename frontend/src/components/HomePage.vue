<template>
  <div class="container has-text-centered">
    <div class="columns is-vcentered">
      <div class="column is-5">
        <figure class="image is-square">
          <img src="../assets/timmy.png" alt="Description">
        </figure>
      </div>
      <div class="column is-6 is-offset-1">
        <h1 class="title is-2">
          Timmy Timesheets
        </h1>
        <h2 class="subtitle is-4">
          Let this cover page describe a product or service.
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
export default {
  name: 'HelloWorld',
  data () {
    return {
      msg: 'Welcome to Your Vue.js App'
    }
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>

</style>
