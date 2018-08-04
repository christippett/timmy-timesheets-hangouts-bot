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
          Configure TimePro
        </h1>
        <h2 class="subtitle is-4">
          Enter your TimePro Timesheets username and password.
        </h2>
        <br>
        <section class="timepro-form">
          <b-field>
            <b-input placeholder="Username" type="email" icon="account">
            </b-input>
          </b-field>
          <b-field>
            <b-input placeholder="Password" type="password" icon="lock">
            </b-input>
          </b-field>
          <div class="control">
            <button class="button is-primary">Submit</button>
          </div>
        </section>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'RegisterConfig',
  beforeCreate: function () {
    var state = this.$route.query.state
    console.log(state)
    if (state === undefined) {
      this.$router.push('/')
    }
  },
  data () {
    return {
      msg: 'Welcome to Your Vue.js App'
    }
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
.timepro-form {
  padding: 0 5rem;
}
</style>
